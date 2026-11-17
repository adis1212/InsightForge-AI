"""Pydantic v2 schemas for Stage 8 Controlled Agentic AI Business Analyst."""
from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class ToolExecutionTrace(BaseModel):
    """Execution step trace for an approved business tool."""
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0
    status: Literal["success", "failed", "insufficient_data", "skipped"] = "success"
    output_summary: str = ""
    error_message: Optional[str] = None


class EvidenceReference(BaseModel):
    """Citation reference returned by the agent (from Pandas KPI or Knowledge Base RAG)."""
    evidence_type: Literal["metric", "forecast", "anomaly", "document"]
    reference_id: str  # e.g. "METRIC:total_revenue" or "DOC-1: vendor_policy.txt"
    title: str
    detail: str
    value: Optional[Any] = None


class ChartPayload(BaseModel):
    """Structured chart data returned by tools for interactive frontend rendering."""
    chart_type: Literal["kpi_grid", "revenue_trends", "product_ranking", "forecast", "anomaly_distribution", "executive_summary"]
    title: str
    subtitle: Optional[str] = None
    data: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
    """A message within the Copilot conversation."""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    intent: Optional[str] = None
    tools_executed: list[str] = Field(default_factory=list)
    execution_trace: list[ToolExecutionTrace] = Field(default_factory=list)
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    chart_payload: Optional[ChartPayload] = None
    structured_report: Optional[dict[str, Any]] = None


class AgentChatRequest(BaseModel):
    """Request payload for the AI Copilot chat endpoint."""
    message: str = Field(..., min_length=2, max_length=2000, description="User business analysis question")
    dataset_id: str = Field(..., description="Target dataset ID or benchmark-wholesale")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID")
    provider_type: Optional[str] = Field("local_demo", description="LLM provider type: local_demo, openai, gemini")
    include_trace: bool = Field(True, description="Whether to include full tool execution trace")


class AgentChatResponse(BaseModel):
    """Response payload from the AI Copilot."""
    session_id: str
    response_text: str
    intent: str
    tools_executed: list[str]
    execution_trace: list[ToolExecutionTrace]
    evidence_references: list[EvidenceReference]
    chart_payload: Optional[ChartPayload] = None
    structured_report: Optional[dict[str, Any]] = None
    is_demo_mode: bool = True
    total_latency_ms: float
    created_at: datetime


class ConversationSessionSummary(BaseModel):
    """Summary of an agent conversation session."""
    session_id: str
    workspace_id: str
    dataset_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
