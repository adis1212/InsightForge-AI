"""Pydantic schemas for datasets."""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class DatasetColumnResponse(BaseModel):
    """Dataset column metadata response."""
    id: str
    name: str
    dtype: str
    mapped_role: Optional[str] = None
    null_count: int = 0
    unique_count: int = 0
    sample_values: Optional[list] = None

    model_config = {"from_attributes": True}


class DatasetResponse(BaseModel):
    """Dataset response."""
    id: str
    workspace_id: str
    name: str
    original_filename: str
    file_size: int
    file_type: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    status: str
    upload_error: Optional[str] = None
    quality_report: Optional[dict] = None
    column_mapping: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetDetailResponse(DatasetResponse):
    """Dataset detail with columns."""
    columns: list[DatasetColumnResponse] = []


class DatasetPreviewResponse(BaseModel):
    """Dataset preview with sample rows."""
    dataset_id: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int


class ColumnMappingUpdate(BaseModel):
    """Update column mapping request."""
    column_mapping: dict[str, str] = Field(
        ...,
        description="Maps standard role names to actual column names"
    )


class QualityReportResponse(BaseModel):
    """Data quality report response."""
    dataset_id: str
    total_rows: int
    total_columns: int
    missing_values: dict[str, int] = {}
    missing_percentages: dict[str, float] = {}
    duplicate_rows: int = 0
    duplicate_percentage: float = 0.0
    date_issues: int = 0
    negative_quantities: int = 0
    zero_prices: int = 0
    cancellation_count: int = 0
    data_quality_score: float = 0.0
