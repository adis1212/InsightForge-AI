"""Stage 7 RAG Retrieval Service.

Provides workspace-scoped document ingestion, chunking, embedding, and semantic retrieval.

RAG DESIGN RULES (enforced in this module):
  - This service NEVER performs financial calculations — it only extracts and retrieves text evidence.
  - Retrieved text is evidence, not an instruction to execute.
  - Prompt-injection patterns embedded in uploaded documents are sanitized before storage.
  - Citations are only returned for chunks that actually exist in the database.
  - Empty results are returned (not errors) when no sufficiently relevant chunks are found.
"""
import re
import time
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.knowledge import DocumentChunk, KnowledgeDocument

UPLOAD_DIR = Path("uploads/knowledge")
MAX_DOCUMENT_SIZE_MB = 25
ALLOWED_DOC_EXTENSIONS = {".pdf", ".txt"}

# Sliding-window chunker parameters
CHUNK_SIZE = 400       # words per chunk
CHUNK_OVERLAP = 60     # word overlap between adjacent chunks

# Minimum cosine similarity to include a chunk in retrieval results
MIN_SIMILARITY = 0.25

# Prompt-injection patterns that must be neutralized in document content
_INJECTION_PATTERNS = [
    re.compile(r"(?i)^ignore (previous|above|all)"),
    re.compile(r"(?i)^forget (everything|prior|your)"),
    re.compile(r"(?i)^you are now"),
    re.compile(r"(?i)^system\s*:"),
    re.compile(r"(?i)^\[system\]"),
    re.compile(r"(?i)^assistant\s*:"),
    re.compile(r"(?i)^<\|.*\|>"),          # common chat-format delimiters
]


class RetrievalService:
    """Lazy-loading embedding model, text extraction, chunking, and semantic retrieval."""

    def __init__(self) -> None:
        self._model = None  # loaded on first use to avoid import overhead at startup

    # ------------------------------------------------------------------
    # Embedding helpers
    # ------------------------------------------------------------------

    def _get_model(self):
        """Lazy-load the sentence-transformer model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Return a list of float-vector embeddings for each input text."""
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Pure-Python cosine similarity using NumPy."""
        import numpy as np  # noqa: PLC0415
        va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
        norm_a, norm_b = float(np.linalg.norm(va)), float(np.linalg.norm(vb))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(va, vb) / (norm_a * norm_b))

    # ------------------------------------------------------------------
    # Text extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text_from_pdf(file_path: Path) -> list[tuple[int, str]]:
        """Extract (page_number, text) pairs from a PDF. page_number is 1-indexed."""
        from pypdf import PdfReader  # noqa: PLC0415
        reader = PdfReader(str(file_path))
        pages: list[tuple[int, str]] = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((i, text))
        return pages

    @staticmethod
    def _extract_text_from_txt(file_path: Path) -> list[tuple[int, str]]:
        """Read a plain-text file; return as single page."""
        text = file_path.read_text(encoding="utf-8", errors="replace")
        return [(1, text)]

    # ------------------------------------------------------------------
    # Security: prompt-injection sanitization
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Remove prompt-injection patterns line by line.

        A line matching any pattern is replaced with a neutral placeholder so the
        surrounding content is preserved but the malicious instruction is neutralised.
        """
        clean_lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if any(p.match(stripped) for p in _INJECTION_PATTERNS):
                clean_lines.append("[CONTENT REMOVED: policy violation]")
            else:
                clean_lines.append(line)
        return "\n".join(clean_lines)

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    @staticmethod
    def _chunk_text(text: str, page_number: int) -> list[dict[str, Any]]:
        """Sliding-window word-level chunker with overlap.

        Returns a list of dicts with keys: chunk_index, chunk_text, page_number, source_reference.
        """
        words = text.split()
        chunks: list[dict[str, Any]] = []
        step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
        idx = 0
        chunk_i = 0
        while idx < len(words):
            window = words[idx: idx + CHUNK_SIZE]
            chunk_text = " ".join(window).strip()
            if len(chunk_text) >= 30:  # skip trivially short fragments
                chunks.append(
                    {
                        "chunk_index": chunk_i,
                        "chunk_text": chunk_text,
                        "page_number": page_number,
                        "source_reference": f"Page {page_number}, chunk {chunk_i + 1}",
                    }
                )
                chunk_i += 1
            idx += step
        return chunks

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest_document(
        self,
        db: Session,
        workspace_id: str,
        file_bytes: bytes,
        original_filename: str,
        title: str,
    ) -> KnowledgeDocument:
        """Validate, extract, chunk, embed, and persist a business document.

        Raises:
            ValueError: on unsupported file type, file too large, or empty extraction.
        """
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_DOC_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext!r}. Allowed: .pdf .txt")
        if len(file_bytes) > MAX_DOCUMENT_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File exceeds {MAX_DOCUMENT_SIZE_MB} MB limit")

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        doc_id = str(uuid.uuid4())
        safe_name = f"{doc_id}{ext}"
        file_path = UPLOAD_DIR / safe_name
        file_path.write_bytes(file_bytes)

        doc = KnowledgeDocument(
            id=doc_id,
            workspace_id=workspace_id,
            title=title,
            original_filename=original_filename,
            file_path=str(file_path),
            file_type=ext.lstrip("."),
            file_size=len(file_bytes),
            status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            if ext == ".pdf":
                pages = self._extract_text_from_pdf(file_path)
            else:
                pages = self._extract_text_from_txt(file_path)

            all_chunk_dicts: list[dict[str, Any]] = []
            for page_no, page_text in pages:
                clean_text = self._sanitize_text(page_text)
                all_chunk_dicts.extend(self._chunk_text(clean_text, page_no))

            if not all_chunk_dicts:
                raise ValueError("No extractable text content found in document")

            texts = [c["chunk_text"] for c in all_chunk_dicts]
            embeddings = self._embed(texts)

            chunk_count = 0
            for chunk_data, emb in zip(all_chunk_dicts, embeddings):
                chunk = DocumentChunk(
                    document_id=doc_id,
                    workspace_id=workspace_id,
                    chunk_index=chunk_data["chunk_index"],
                    chunk_text=chunk_data["chunk_text"],
                    embedding=emb,
                    page_number=chunk_data["page_number"],
                    source_reference=chunk_data["source_reference"],
                )
                db.add(chunk)
                chunk_count += 1

            doc.status = "ready"
            doc.chunk_count = chunk_count
            db.commit()
            db.refresh(doc)

        except Exception as exc:
            doc.status = "error"
            doc.error_message = str(exc)[:500]
            db.commit()
            raise

        return doc

    def retrieve(
        self,
        db: Session,
        workspace_id: str,
        query: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Retrieve top-k most relevant chunks for query, enforcing workspace isolation.

        Returns a dict matching the RetrievalResponse schema.
        Only chunks from documents owned by workspace_id are ever considered.
        """
        t0 = time.perf_counter()
        query_emb = self._embed([query])[0]

        # Workspace-scoped chunk lookup — cross-workspace isolation enforced here
        chunks: list[DocumentChunk] = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.workspace_id == workspace_id)
            .all()
        )

        scored: list[tuple[float, DocumentChunk]] = []
        for chunk in chunks:
            if chunk.embedding:
                score = self._cosine_similarity(query_emb, chunk.embedding)
                if score >= MIN_SIMILARITY:
                    scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        latency_ms = (time.perf_counter() - t0) * 1000

        result_chunks: list[dict[str, Any]] = []
        for score, chunk in top:
            result_chunks.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": chunk.document.title if chunk.document else "Unknown",
                    "chunk_index": chunk.chunk_index,
                    "chunk_text": chunk.chunk_text[:500],
                    "page_number": chunk.page_number,
                    "source_reference": chunk.source_reference,
                    "similarity_score": round(score, 4),
                }
            )

        if not result_chunks:
            evidence_summary = "No relevant business documents found in knowledge base."
        else:
            citations = "; ".join(
                f'[{r["document_title"]}, {r["source_reference"]}]'
                for r in result_chunks
            )
            evidence_summary = (
                f"Retrieved {len(result_chunks)} evidence passage(s) from workspace knowledge base: {citations}"
            )

        return {
            "query": query,
            "workspace_id": workspace_id,
            "chunks_found": len(result_chunks),
            "retrieved_chunks": result_chunks,
            "retrieval_latency_ms": round(latency_ms, 2),
            "evidence_summary": evidence_summary,
        }

    def delete_document(self, db: Session, workspace_id: str, document_id: str) -> bool:
        """Delete a document and all associated chunks. Workspace-scoped.

        Returns True if the document was found and deleted; False if not found.
        """
        doc: KnowledgeDocument | None = (
            db.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.id == document_id,
                KnowledgeDocument.workspace_id == workspace_id,
            )
            .first()
        )
        if not doc:
            return False

        # Best-effort file removal
        try:
            Path(doc.file_path).unlink(missing_ok=True)
        except Exception:
            pass

        db.delete(doc)  # cascades to DocumentChunk
        db.commit()
        return True

    def list_documents(self, db: Session, workspace_id: str) -> list[KnowledgeDocument]:
        """Return all documents owned by workspace_id, newest first."""
        return (
            db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.workspace_id == workspace_id)
            .order_by(KnowledgeDocument.created_at.desc())
            .all()
        )

    def get_document(self, db: Session, workspace_id: str, document_id: str) -> KnowledgeDocument | None:
        """Return a single document, enforcing workspace ownership."""
        return (
            db.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.id == document_id,
                KnowledgeDocument.workspace_id == workspace_id,
            )
            .first()
        )


# Singleton — shared across the application
retrieval_service = RetrievalService()
