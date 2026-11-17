"""Agent database models for Stage 8 Controlled Agentic AI Business Analyst."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class AgentSession(Base):
    """Conversation session with the AI Copilot."""
    __tablename__ = "agent_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(String, nullable=False)
    title = Column(String, nullable=False, default="Business Analysis Session")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    messages = relationship("AgentMessageRecord", back_populates="session", cascade="all, delete-orphan", order_by="AgentMessageRecord.created_at")


class AgentMessageRecord(Base):
    """A single message record in an agent session."""
    __tablename__ = "agent_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    tools_executed = Column(JSON, nullable=True)  # list[str]
    execution_trace = Column(JSON, nullable=True)  # list[dict]
    evidence_references = Column(JSON, nullable=True)  # list[dict]
    chart_payload = Column(JSON, nullable=True)  # dict
    structured_report = Column(JSON, nullable=True)  # dict
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("AgentSession", back_populates="messages")
