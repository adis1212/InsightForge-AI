"""Dataset database model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dataset(Base):
    """Uploaded dataset model."""

    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    file_type = Column(String, nullable=False)  # csv, xlsx
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, processing, ready, error
    upload_error = Column(String, nullable=True)

    # Data quality metadata
    quality_report = Column(JSON, nullable=True)
    column_mapping = Column(JSON, nullable=True)  # maps standard names to actual column names

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="datasets")
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    kpi_results = relationship("KPIResult", back_populates="dataset", cascade="all, delete-orphan")


class DatasetColumn(Base):
    """Metadata about individual dataset columns."""

    __tablename__ = "dataset_columns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    dtype = Column(String, nullable=False)  # inferred pandas dtype
    mapped_role = Column(String, nullable=True)  # e.g., "invoice_no", "quantity", "unit_price", "customer_id", "country", "date", "description", "stock_code"
    null_count = Column(Integer, default=0)
    unique_count = Column(Integer, default=0)
    sample_values = Column(JSON, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="columns")


class KPIResult(Base):
    """Cached KPI calculation results."""

    __tablename__ = "kpi_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    kpi_name = Column(String, nullable=False)
    kpi_value = Column(Float, nullable=True)
    kpi_metadata = Column(JSON, nullable=True)  # additional context (e.g., breakdown data)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    dataset = relationship("Dataset", back_populates="kpi_results")
