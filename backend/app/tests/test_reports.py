"""Tests for Stage 9 Executive PDF Report Generation."""
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.database import Base, engine, SessionLocal
from app.main import create_app
from app.models.report import ReportRecord  # noqa: F401
from app.schemas.report_schemas import ReportGenerateRequest
from app.services.report_service import report_service

# Ensure all database tables including reports exist
Base.metadata.create_all(bind=engine)

app = create_app()
client = TestClient(app)


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestReportGenerationService:
    """Unit tests for ReportLab PDF generator."""

    def test_generate_pdf_report_benchmark_success(self, db: Session):
        req = ReportGenerateRequest(
            dataset_id="benchmark-wholesale",
            prompt_version="v2",
            title="Boardroom Commercial Briefing FY2023",
            include_forecast=True,
            include_anomalies=True,
            include_rag=True,
        )
        record = report_service.generate_report(
            db=db,
            workspace_id="demo-workspace-01",
            request=req,
        )

        assert record.id is not None
        assert record.format == "pdf"
        assert record.status == "ready"
        assert record.file_size_bytes > 5000
        assert os.path.exists(record.file_path)

        # Inspect report metadata snapshot
        meta = record.report_metadata
        assert meta is not None
        assert meta["total_revenue"] > 0
        assert meta["prompt_version"] == "v2"
        assert meta["has_forecast"] is True
        assert meta["has_anomalies"] is True

    def test_pdf_structure_and_readability(self, db: Session):
        req = ReportGenerateRequest(
            dataset_id="benchmark-wholesale",
            prompt_version="v2",
            title="Structural PDF Verification",
            include_forecast=True,
            include_anomalies=True,
            include_rag=True,
        )
        record = report_service.generate_report(
            db=db,
            workspace_id="demo-workspace-01",
            request=req,
        )

        # Validate with pypdf
        reader = PdfReader(record.file_path)
        assert len(reader.pages) >= 2  # Multi-page executive briefing

        full_text = " ".join(page.extract_text() or "" for page in reader.pages)
        assert "INSIGHTFORGE AI" in full_text
        assert "Commercial KPI Scorecard" in full_text
        assert "Total Net Revenue" in full_text

    def test_missing_dataset_raises_value_error(self, db: Session):
        req = ReportGenerateRequest(
            dataset_id="nonexistent-dataset-id",
            prompt_version="v2",
        )
        with pytest.raises(ValueError) as exc_info:
            report_service.generate_report(
                db=db,
                workspace_id="demo-workspace-01",
                request=req,
            )
        assert "not found" in str(exc_info.value).lower()


class TestReportAPIEndpoints:
    """Integration tests for report REST API endpoints."""

    def test_generate_report_via_api(self):
        resp = client.post(
            "/api/v1/workspaces/demo-workspace-01/reports/generate",
            json={
                "dataset_id": "benchmark-wholesale",
                "prompt_version": "v2",
                "title": "API Generated Board Report",
                "include_forecast": True,
                "include_anomalies": True,
                "include_rag": True,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] is not None
        assert data["status"] == "ready"
        assert "download_url" in data
        assert data["file_size_bytes"] > 5000

        report_id = data["id"]

        # Test list endpoint
        list_resp = client.get("/api/v1/workspaces/demo-workspace-01/reports/")
        assert list_resp.status_code == 200
        reports = list_resp.json()
        assert any(r["id"] == report_id for r in reports)

        # Test detail endpoint
        get_resp = client.get(f"/api/v1/workspaces/demo-workspace-01/reports/{report_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == report_id

        # Test download endpoint
        dl_resp = client.get(f"/api/v1/workspaces/demo-workspace-01/reports/{report_id}/download")
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "application/pdf"
        assert len(dl_resp.content) > 5000

        # Test delete endpoint
        del_resp = client.delete(f"/api/v1/workspaces/demo-workspace-01/reports/{report_id}")
        assert del_resp.status_code == 204

        # Verify 404 after deletion
        get_after_del = client.get(f"/api/v1/workspaces/demo-workspace-01/reports/{report_id}")
        assert get_after_del.status_code == 404
