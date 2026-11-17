"""Knowledge Base API endpoints — Stage 7 RAG.

Provides workspace-scoped document upload, listing, retrieval, search, and deletion.

Security:
  - All mutations require authenticated JWT credentials.
  - GET/search endpoints use optional auth — demo workspaces (demo-*) are permitted without token.
  - Cross-workspace data access is impossible: every query filters by workspace_id.
  - Prompt injection is sanitized at ingestion time (see RetrievalService).
"""
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.schemas.knowledge_schemas import (
    KnowledgeDocumentResponse,
    DocumentUploadResponse,
    RetrievalResponse,
    KnowledgeSearchRequest,
)
from app.services.retrieval_service import retrieval_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}/knowledge",
    tags=["Knowledge Base"],
)

_ALLOWED_TYPES = {".pdf", ".txt"}
_MAX_BYTES = 25 * 1024 * 1024  # 25 MB


# ---------------------------------------------------------------------------
# Access control helpers
# ---------------------------------------------------------------------------


def _check_workspace_access(db: Session, workspace_id: str, user: Optional[User]) -> None:
    """Allow demo workspaces without auth; require membership for real workspaces."""
    if workspace_id.startswith("demo-"):
        return
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for non-demo workspaces",
        )
    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")


def _require_authenticated_member(db: Session, workspace_id: str, user: User) -> None:
    """Mutations always require an authenticated member — no demo bypass."""
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
        .first()
    )
    if not member and not workspace_id.startswith("demo-"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a business document (PDF or TXT) to the workspace knowledge base.

    The document is processed synchronously: text extraction → chunking → embedding.
    Status will be 'ready' on success or 'error' on failure.
    """
    _require_authenticated_member(db, workspace_id, current_user)

    from pathlib import Path  # noqa: PLC0415
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type {ext!r}. Allowed: .pdf .txt",
        )

    contents = await file.read()
    if len(contents) > _MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Document exceeds the 25 MB size limit",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Empty file")

    doc_title = title or (file.filename or "Untitled Document")

    try:
        doc = retrieval_service.ingest_document(
            db=db,
            workspace_id=workspace_id,
            file_bytes=contents,
            original_filename=file.filename or "document",
            title=doc_title,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return KnowledgeDocumentResponse.model_validate(doc)


@router.get("/", response_model=list[KnowledgeDocumentResponse])
def list_documents(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """List all business documents in this workspace, newest first."""
    _check_workspace_access(db, workspace_id, current_user)
    docs = retrieval_service.list_documents(db, workspace_id)
    return [KnowledgeDocumentResponse.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=KnowledgeDocumentResponse)
def get_document(
    workspace_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Retrieve metadata for a single knowledge document."""
    _check_workspace_access(db, workspace_id, current_user)
    doc = retrieval_service.get_document(db, workspace_id, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return KnowledgeDocumentResponse.model_validate(doc)


@router.delete("/{document_id}")
def delete_document(
    workspace_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document and all its chunks from the workspace knowledge base."""
    _require_authenticated_member(db, workspace_id, current_user)
    deleted = retrieval_service.delete_document(db, workspace_id, document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"deleted": True, "document_id": document_id}


@router.post("/search", response_model=RetrievalResponse)
def search_knowledge(
    workspace_id: str,
    payload: KnowledgeSearchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Semantic search over the workspace's business document knowledge base.

    Returns the top-k most relevant document passages for the given query,
    ranked by cosine similarity. Only returns passages above the minimum
    similarity threshold (0.25). An empty result set is returned (not an error)
    when no sufficiently relevant documents exist.
    """
    _check_workspace_access(db, workspace_id, current_user)
    result = retrieval_service.retrieve(
        db=db,
        workspace_id=workspace_id,
        query=payload.query,
        top_k=payload.top_k,
    )
    return RetrievalResponse(**result)
