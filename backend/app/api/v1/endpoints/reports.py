"""Executive PDF Report API Endpoints — Stage 9."""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user_optional
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.report import ReportRecord
from app.schemas.report_schemas import (
    ReportGenerateRequest,
    ReportSummary,
    ReportDetail,
)
from app.services.report_service import report_service

router = APIRouter(
    prefix="/workspaces/{workspace_id}/reports",
    tags=["Executive Reports"],
)


def _check_workspace_access(db: Session, workspace_id: str, user: Optional[User]) -> None:
    """Verify workspace membership with unauthenticated bypass for demo workspaces."""
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )


@router.post("/generate", response_model=ReportDetail, status_code=status.HTTP_201_CREATED)
def generate_report(
    workspace_id: str,
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Generate an executive commercial PDF report from verified analytics, ML, RAG, and prompt results.
    """
    _check_workspace_access(db, workspace_id, current_user)

    try:
        record = report_service.generate_report(
            db=db,
            workspace_id=workspace_id,
            request=payload,
        )
        download_url = f"/api/v1/workspaces/{workspace_id}/reports/{record.id}/download"
        return ReportDetail(
            id=record.id,
            workspace_id=record.workspace_id,
            dataset_id=record.dataset_id,
            title=record.title,
            prompt_version=record.prompt_version,
            file_size_bytes=record.file_size_bytes,
            format=record.format,
            status=record.status,
            download_url=download_url,
            report_metadata=record.report_metadata,
            created_at=record.created_at,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err)) from val_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {exc}",
        ) from exc


@router.get("/", response_model=list[ReportSummary])
def list_reports(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """List all generated executive reports in this workspace."""
    _check_workspace_access(db, workspace_id, current_user)

    reports = (
        db.query(ReportRecord)
        .filter(ReportRecord.workspace_id == workspace_id)
        .order_by(ReportRecord.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        ReportSummary(
            id=r.id,
            workspace_id=r.workspace_id,
            dataset_id=r.dataset_id,
            title=r.title,
            prompt_version=r.prompt_version,
            file_size_bytes=r.file_size_bytes,
            format=r.format,
            status=r.status,
            created_at=r.created_at,
        )
        for r in reports
    ]


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(
    workspace_id: str,
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get metadata for a specific executive report."""
    _check_workspace_access(db, workspace_id, current_user)

    record = (
        db.query(ReportRecord)
        .filter(ReportRecord.id == report_id, ReportRecord.workspace_id == workspace_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    download_url = f"/api/v1/workspaces/{workspace_id}/reports/{record.id}/download"
    return ReportDetail(
        id=record.id,
        workspace_id=record.workspace_id,
        dataset_id=record.dataset_id,
        title=record.title,
        prompt_version=record.prompt_version,
        file_size_bytes=record.file_size_bytes,
        format=record.format,
        status=record.status,
        download_url=download_url,
        report_metadata=record.report_metadata,
        created_at=record.created_at,
    )


@router.get("/{report_id}/download")
def download_report(
    workspace_id: str,
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Download the binary PDF file."""
    _check_workspace_access(db, workspace_id, current_user)

    record = (
        db.query(ReportRecord)
        .filter(ReportRecord.id == report_id, ReportRecord.workspace_id == workspace_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if not os.path.exists(record.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file missing from disk")

    safe_title = "".join(c for c in record.title if c.isalnum() or c in (" ", "-", "_")).strip()
    safe_filename = f"{safe_title.replace(' ', '_')}_{record.id[:8]}.pdf"

    return FileResponse(
        path=record.file_path,
        media_type="application/pdf",
        filename=safe_filename,
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    workspace_id: str,
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Delete a report record and its physical PDF file."""
    _check_workspace_access(db, workspace_id, current_user)

    record = (
        db.query(ReportRecord)
        .filter(ReportRecord.id == report_id, ReportRecord.workspace_id == workspace_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if os.path.exists(record.file_path):
        try:
            os.remove(record.file_path)
        except OSError as e:
            logger.warning(f"Could not delete physical report file {record.file_path}: {e}")

    db.delete(record)
    db.commit()
    return None
