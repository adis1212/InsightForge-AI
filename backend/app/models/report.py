"""SQLAlchemy model for Stage 9 Executive PDF Reports."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReportRecord(Base):
    """Generated executive PDF commercial report record."""
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(String, nullable=False)
    title = Column(String, nullable=False, default="Executive Commercial Report")
    prompt_version = Column(String, nullable=False, default="v2")
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False, default=0)
    format = Column(String, nullable=False, default="pdf")
    status = Column(String, nullable=False, default="ready")  # "generating" | "ready" | "failed"
    error_message = Column(Text, nullable=True)

    # Structured metadata snapshot
    report_metadata = Column(JSON, nullable=True)  # KPIs, forecast summary, anomaly counts, verification status

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
