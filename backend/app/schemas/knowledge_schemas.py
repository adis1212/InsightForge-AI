"""Pydantic v2 schemas for Stage 7 Knowledge Base RAG."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocumentResponse(BaseModel):
    """Public representation of a business knowledge document."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    title: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime


class DocumentUploadResponse(KnowledgeDocumentResponse):
    """Returned immediately after a document upload is accepted."""
    pass


class ChunkResult(BaseModel):
    """A single retrieved document passage with provenance metadata."""

    chunk_id: str
    document_id: str
    document_title: str
    chunk_index: int
    chunk_text: str  # truncated to 500 chars in API responses
    page_number: Optional[int] = None
    source_reference: Optional[str] = None
    similarity_score: float


class RetrievalResponse(BaseModel):
    """Full retrieval result for a business knowledge query."""

    query: str
    workspace_id: str
    chunks_found: int
    retrieved_chunks: list[ChunkResult]
    retrieval_latency_ms: float
    evidence_summary: str  # formatted citation string for display & LLM context injection


class KnowledgeSearchRequest(BaseModel):
    """Body for POST /knowledge/search."""

    query: str = Field(..., min_length=3, description="Minimum 3-character search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of top chunks to return (max 20)")
