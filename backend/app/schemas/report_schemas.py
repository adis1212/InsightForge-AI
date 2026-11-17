"""Pydantic v2 schemas for Stage 9 Executive Report Generation."""
from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    """Payload to request executive report generation."""
    dataset_id: str = Field(..., description="Target dataset ID (e.g. benchmark-wholesale or UUID)")
    prompt_version: Literal["v1", "v2"] = Field("v2", description="Prompt engine version to ground narrative")
    title: Optional[str] = Field(None, description="Custom executive report title")
    include_forecast: bool = Field(True, description="Include XGBoost sales forecast chart & metrics")
    include_anomalies: bool = Field(True, description="Include Isolation Forest transaction anomaly screening")
    include_rag: bool = Field(True, description="Include retrieved business policy citations")


class ReportSummary(BaseModel):
    """Brief summary item of a generated report."""
    id: str
    workspace_id: str
    dataset_id: str
    title: str
    prompt_version: str
    file_size_bytes: int
    format: str
    status: str
    created_at: datetime


class ReportDetail(BaseModel):
    """Detailed metadata and download reference for a report."""
    id: str
    workspace_id: str
    dataset_id: str
    title: str
    prompt_version: str
    file_size_bytes: int
    format: str
    status: str
    download_url: str
    report_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
