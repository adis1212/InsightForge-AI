"""Dataset upload and management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import FileUploadError, ValidationError
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.dataset import Dataset, DatasetColumn
from app.schemas.dataset import (
    DatasetResponse, DatasetDetailResponse, DatasetPreviewResponse,
    ColumnMappingUpdate, QualityReportResponse,
)
from app.services.dataset_service import (
    validate_file, save_upload, read_dataset,
    auto_detect_columns, analyze_quality, get_column_metadata,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/datasets", tags=["Datasets"])


def _check_workspace_access(db: Session, workspace_id: str, user_id: str):
    """Verify workspace membership."""
    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")
    return member


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    workspace_id: str,
    file: UploadFile = File(...),
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a CSV or XLSX dataset."""
    _check_workspace_access(db, workspace_id, current_user.id)

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate
    try:
        validate_file(file.filename or "unknown", file_size)
    except FileUploadError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    # Save to disk
    file_path = save_upload(content, file.filename or "upload.csv", workspace_id)

    # Parse and analyze
    try:
        df = read_dataset(file_path)
        column_mapping = auto_detect_columns(df)
        quality = analyze_quality(df, column_mapping)
        columns_meta = get_column_metadata(df, column_mapping)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)

    # Create dataset record
    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "csv"
    dataset = Dataset(
        workspace_id=workspace_id,
        name=name or file.filename or "Untitled Dataset",
        original_filename=file.filename or "upload",
        file_path=file_path,
        file_size=file_size,
        file_type=ext.lower(),
        row_count=len(df),
        column_count=len(df.columns),
        status="ready",
        quality_report=quality,
        column_mapping=column_mapping,
    )
    db.add(dataset)
    db.flush()

    # Save column metadata
    for col_meta in columns_meta:
        col = DatasetColumn(
            dataset_id=dataset.id,
            name=col_meta["name"],
            dtype=col_meta["dtype"],
            mapped_role=col_meta.get("mapped_role"),
            null_count=col_meta["null_count"],
            unique_count=col_meta["unique_count"],
            sample_values=col_meta["sample_values"],
        )
        db.add(col)

    db.commit()
    db.refresh(dataset)

    return DatasetResponse.model_validate(dataset)


@router.get("/", response_model=list[DatasetResponse])
def list_datasets(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all datasets in a workspace."""
    _check_workspace_access(db, workspace_id, current_user.id)
    datasets = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).all()
    return [DatasetResponse.model_validate(ds) for ds in datasets]


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dataset details with column metadata."""
    _check_workspace_access(db, workspace_id, current_user.id)
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    return DatasetDetailResponse.model_validate(dataset)


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(
    workspace_id: str,
    dataset_id: str,
    rows: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview dataset rows."""
    _check_workspace_access(db, workspace_id, current_user.id)
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    df = read_dataset(dataset.file_path)
    preview_df = df.head(rows)

    # Convert to JSON-safe format
    preview_rows = []
    for _, row in preview_df.iterrows():
        row_dict = {}
        for col in preview_df.columns:
            val = row[col]
            if hasattr(val, "item"):
                val = val.item()
            elif hasattr(val, "isoformat"):
                val = val.isoformat()
            elif not isinstance(val, (str, int, float, bool, type(None))):
                val = str(val)
            row_dict[col] = val
        preview_rows.append(row_dict)

    return DatasetPreviewResponse(
        dataset_id=dataset.id,
        columns=list(preview_df.columns),
        rows=preview_rows,
        total_rows=dataset.row_count or len(df),
    )


@router.put("/{dataset_id}/mapping", response_model=DatasetDetailResponse)
def update_column_mapping(
    workspace_id: str,
    dataset_id: str,
    payload: ColumnMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update column role mapping for a dataset."""
    _check_workspace_access(db, workspace_id, current_user.id)
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    dataset.column_mapping = payload.column_mapping

    # Re-analyze quality with new mapping
    df = read_dataset(dataset.file_path)
    dataset.quality_report = analyze_quality(df, payload.column_mapping)

    # Update column roles
    reverse_mapping = {v: k for k, v in payload.column_mapping.items()}
    for col in dataset.columns:
        col.mapped_role = reverse_mapping.get(col.name)

    db.commit()
    db.refresh(dataset)

    return DatasetDetailResponse.model_validate(dataset)


@router.get("/{dataset_id}/quality", response_model=QualityReportResponse)
def get_quality_report(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get data quality report for a dataset."""
    _check_workspace_access(db, workspace_id, current_user.id)
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    if not dataset.quality_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality report not available. Re-upload or reprocess the dataset.",
        )

    return QualityReportResponse(dataset_id=dataset.id, **dataset.quality_report)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a dataset."""
    _check_workspace_access(db, workspace_id, current_user.id)
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    db.delete(dataset)
    db.commit()
