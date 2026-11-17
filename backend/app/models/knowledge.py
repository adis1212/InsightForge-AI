"""Knowledge Base database models for Stage 7 RAG."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class KnowledgeDocument(Base):
    """Uploaded business document (PDF or TXT) for RAG retrieval."""

    __tablename__ = "knowledge_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "pdf" or "txt"
    file_size = Column(Integer, nullable=False)  # bytes
    status = Column(String, default="processing")  # processing | ready | error
    error_message = Column(String, nullable=True)
    chunk_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """A single text chunk extracted from a KnowledgeDocument, with its embedding vector."""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(String, nullable=False, index=True)  # denormalised for fast workspace-scoped queries
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # list[float] — stored as JSON; SQLite-compatible
    page_number = Column(Integer, nullable=True)
    source_reference = Column(String, nullable=True)  # e.g. "Page 3, chunk 2"

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("KnowledgeDocument", back_populates="chunks")
