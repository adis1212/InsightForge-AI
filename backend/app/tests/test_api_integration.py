"""Full API integration tests with SQLite in-memory database."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import io

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole

# Create SQLite in-memory engine for integration tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "InsightForge" in data["app"]


class TestAuthEndpoints:
    """Test user registration and login workflows."""

    def test_register_and_login_success(self, client):
        # 1. Register
        reg_payload = {
            "email": "analyst@example.com",
            "full_name": "Test Analyst",
            "password": "SecurePassword123!",
        }
        res = client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "analyst@example.com"
        assert data["user"]["full_name"] == "Test Analyst"

        token = data["access_token"]

        # 2. Get profile /me
        me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "analyst@example.com"

        # 3. Login
        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@example.com", "password": "SecurePassword123!"},
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

    def test_duplicate_registration_fails(self, client):
        reg_payload = {
            "email": "dup@example.com",
            "full_name": "Duplicate User",
            "password": "Password123!",
        }
        client.post("/api/v1/auth/register", json=reg_payload)
        res = client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 409
        assert "already registered" in res.json()["detail"].lower()

    def test_invalid_login_password(self, client):
        reg_payload = {
            "email": "user@example.com",
            "full_name": "Normal User",
            "password": "CorrectPassword123!",
        }
        client.post("/api/v1/auth/register", json=reg_payload)

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "WrongPassword!"},
        )
        assert res.status_code == 401


class TestWorkspaceEndpoints:
    """Test workspace creation and multi-tenant authorization."""

    @pytest.fixture
    def auth_headers(self, client):
        reg_payload = {
            "email": "owner@company.com",
            "full_name": "Company Owner",
            "password": "Password123!",
        }
        res = client.post("/api/v1/auth/register", json=reg_payload)
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def second_user_headers(self, client):
        reg_payload = {
            "email": "outsider@other.com",
            "full_name": "Outsider User",
            "password": "Password123!",
        }
        res = client.post("/api/v1/auth/register", json=reg_payload)
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_and_list_workspace(self, client, auth_headers):
        ws_payload = {"name": "European Wholesale Hub", "description": "Operations in DE and FR"}
        res = client.post("/api/v1/workspaces/", json=ws_payload, headers=auth_headers)
        assert res.status_code == 201
        ws_data = res.json()
        assert ws_data["name"] == "European Wholesale Hub"
        assert ws_data["user_role"] == "owner"

        list_res = client.get("/api/v1/workspaces/", headers=auth_headers)
        assert list_res.status_code == 200
        workspaces = list_res.json()
        assert len(workspaces) == 1
        assert workspaces[0]["id"] == ws_data["id"]

    def test_workspace_isolation_forbidden(self, client, auth_headers, second_user_headers):
        # Create workspace with User 1
        res = client.post(
            "/api/v1/workspaces/",
            json={"name": "Confidential Workspace"},
            headers=auth_headers,
        )
        ws_id = res.json()["id"]

        # User 2 attempts to access it -> 403 Forbidden
        unauth_res = client.get(f"/api/v1/workspaces/{ws_id}", headers=second_user_headers)
        assert unauth_res.status_code == 403
        assert "not a member" in unauth_res.json()["detail"].lower()


class TestDatasetAndAnalyticsAPI:
    """Test dataset upload and analytics endpoint execution via HTTP."""

    @pytest.fixture
    def setup_workspace(self, client):
        # Register user
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "data@analytics.com", "full_name": "Data Lead", "password": "Password123!"},
        )
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create workspace
        ws_res = client.post(
            "/api/v1/workspaces/",
            json={"name": "Analytics Lab"},
            headers=headers,
        )
        ws_id = ws_res.json()["id"]
        return headers, ws_id

    def test_upload_and_analyze_dataset(self, client, setup_workspace):
        headers, ws_id = setup_workspace

        csv_content = (
            "Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country\n"
            "5001,ITEM1,Product 1,10,2023-01-10 10:00:00,20.00,CUST1,United Kingdom\n"
            "5002,ITEM2,Product 2,5,2023-02-15 11:30:00,50.00,CUST2,Germany\n"
            "C5003,ITEM1,Product 1,-2,2023-02-18 12:00:00,20.00,CUST1,United Kingdom\n"
        )

        files = {"file": ("test_wholesale.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        # 1. Upload dataset
        upload_res = client.post(
            f"/api/v1/workspaces/{ws_id}/datasets/upload",
            files=files,
            data={"name": "Test Wholesale Ingestion"},
            headers=headers,
        )
        assert upload_res.status_code == 201
        dataset_data = upload_res.json()
        assert dataset_data["row_count"] == 3
        assert dataset_data["column_count"] == 8
        ds_id = dataset_data["id"]

        # 2. Preview dataset
        preview_res = client.get(
            f"/api/v1/workspaces/{ws_id}/datasets/{ds_id}/preview",
            headers=headers,
        )
        assert preview_res.status_code == 200
        preview_data = preview_res.json()
        assert len(preview_data["rows"]) == 3

        # 3. Quality report
        quality_res = client.get(
            f"/api/v1/workspaces/{ws_id}/datasets/{ds_id}/quality",
            headers=headers,
        )
        assert quality_res.status_code == 200
        quality_data = quality_res.json()
        assert quality_data["cancellation_count"] == 1
        assert quality_data["negative_quantities"] == 1

        # 4. Analytics KPI Summary
        summary_res = client.get(
            f"/api/v1/workspaces/{ws_id}/analytics/{ds_id}/summary",
            headers=headers,
        )
        assert summary_res.status_code == 200
        summary_data = summary_res.json()
        # Revenue: (10 * 20.00) + (5 * 50.00) = 200 + 250 = 450.00 (excluding cancellation)
        assert summary_data["total_revenue"]["value"] == 450.00
        assert summary_data["unique_orders"]["value"] == 2.0

        # 5. Full analytics
        full_res = client.get(
            f"/api/v1/workspaces/{ws_id}/analytics/{ds_id}",
            headers=headers,
        )
        assert full_res.status_code == 200
        full_data = full_res.json()
        assert len(full_data["monthly_revenue"]) == 2
        assert len(full_data["top_products"]) == 2

        # 6. Machine Learning Intelligence Endpoints
        # For 3-row dataset, verify graceful insufficient_data response
        forecast_res = client.get(
            f"/api/v1/workspaces/{ws_id}/analytics/{ds_id}/forecast",
            headers=headers,
        )
        assert forecast_res.status_code == 200
        assert forecast_res.json()["status"] == "insufficient_data"

        anomaly_res = client.get(
            f"/api/v1/workspaces/{ws_id}/analytics/{ds_id}/anomalies",
            headers=headers,
        )
        assert anomaly_res.status_code == 200
        assert anomaly_res.json()["status"] == "insufficient_data"

        # Verify ML endpoints on benchmark wholesale dataset (5,015 rows)
        bench_forecast_res = client.get(
            f"/api/v1/workspaces/{ws_id}/analytics/benchmark-wholesale/forecast",
            headers=headers,
        )
        assert bench_forecast_res.status_code == 200
        bench_forecast_data = bench_forecast_res.json()
        assert bench_forecast_data["status"] == "success"
        assert bench_forecast_data["forecast_horizon_periods"] == 6
        assert bench_forecast_data["evaluation"] is not None
        assert "wape" in bench_forecast_data["evaluation"]["xgboost_metrics"]

        bench_anomaly_res = client.get(
            f"/api/v1/workspaces/{ws_id}/analytics/benchmark-wholesale/anomalies",
            headers=headers,
        )
        assert bench_anomaly_res.status_code == 200
        bench_anomaly_data = bench_anomaly_res.json()
        assert bench_anomaly_data["status"] == "success"
        assert bench_anomaly_data["total_records_analyzed"] > 5000
        assert bench_anomaly_data["anomaly_count"] > 0
        assert len(bench_anomaly_data["flagged_anomalies"]) > 0
        # 7. Prompt Engine API tests
        # Templates inspection
        tmpl_res = client.get(
            f"/api/v1/workspaces/{ws_id}/prompts/templates",
            headers=headers,
        )
        assert tmpl_res.status_code == 200
        assert "prompt1_factual_v2.jinja2" in tmpl_res.json()["templates"]

        # Prompt chain execution
        exec_res = client.post(
            f"/api/v1/workspaces/{ws_id}/prompts/execute",
            json={"dataset_id": ds_id, "prompt_version": "v2", "provider_type": "local_demo"},
            headers=headers,
        )
        assert exec_res.status_code == 200
        chain_data = exec_res.json()
        assert chain_data["prompt_version"] == "v2"
        assert chain_data["overall_accuracy_score"] == 100.0
        assert chain_data["structured_report"] is not None

        # Prompt comparison v1 vs v2
        comp_res = client.post(
            f"/api/v1/workspaces/{ws_id}/prompts/compare",
            json={"dataset_id": ds_id, "provider_type": "local_demo"},
            headers=headers,
        )
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert "v1_result" in comp_data
        assert "v2_result" in comp_data
        assert "Prompt v2 improved" in comp_data["comparison_summary"]

        # Prompt evaluation scorecard
        eval_res = client.get(
            f"/api/v1/workspaces/{ws_id}/prompts/evaluation",
            headers=headers,
        )
        assert eval_res.status_code == 200
        scorecard_data = eval_res.json()
        assert scorecard_data["v2_avg_accuracy"] >= scorecard_data["v1_avg_accuracy"]

        # 8. Knowledge Base Document Ingestion & RAG retrieval
        txt_content = (
            "COMMERCIAL RETURN POLICY\n"
            "Restocking fee of 15% applies on all returned goods.\n"
            "Payment terms are strictly Net 30 days.\n"
            "Minimum wholesale order size is 50 units.\n"
        )
        doc_files = {"file": ("vendor_policy.txt", io.BytesIO(txt_content.encode("utf-8")), "text/plain")}
        doc_upload_res = client.post(
            f"/api/v1/workspaces/{ws_id}/knowledge/upload",
            files=doc_files,
            data={"title": "Wholesale Return Policy"},
            headers=headers,
        )
        assert doc_upload_res.status_code == 201
        doc_data = doc_upload_res.json()
        assert doc_data["title"] == "Wholesale Return Policy"
        assert doc_data["status"] == "ready"
        assert doc_data["chunk_count"] >= 1
        knowledge_doc_id = doc_data["id"]

        # List documents
        list_res = client.get(f"/api/v1/workspaces/{ws_id}/knowledge/", headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1

        # Search documents
        search_res = client.post(
            f"/api/v1/workspaces/{ws_id}/knowledge/search",
            json={"query": "restocking fee payment terms", "top_k": 3},
            headers=headers,
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["chunks_found"] >= 1
        assert "Wholesale Return Policy" in search_data["evidence_summary"]

        # Delete document
        del_res = client.delete(
            f"/api/v1/workspaces/{ws_id}/knowledge/{knowledge_doc_id}",
            headers=headers,
        )
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True


class TestDemoModeUnauthenticatedAccess:
    """Test that zero-cost demo exploration works without authentication tokens."""

    def test_demo_prompt_chain_execution_unauthenticated(self, client):
        res = client.post(
            "/api/v1/workspaces/demo-workspace-01/prompts/execute",
            json={
                "dataset_id": "benchmark-wholesale",
                "prompt_version": "v2",
                "provider_type": "local_demo",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["is_demo_mode"] is True
        assert data["overall_accuracy_score"] == 100.0
        assert data["structured_report"] is not None

    def test_demo_prompt_comparison_unauthenticated(self, client):
        res = client.post(
            "/api/v1/workspaces/demo-workspace-01/prompts/compare",
            json={
                "dataset_id": "benchmark-wholesale",
                "provider_type": "local_demo",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["v2_result"]["overall_accuracy_score"] == 100.0
        assert data["accuracy_delta"] > 0

    def test_demo_prompt_templates_unauthenticated(self, client):
        res = client.get("/api/v1/workspaces/demo-workspace-01/prompts/templates")
        assert res.status_code == 200
        assert "templates" in res.json()

    def test_demo_evaluation_scorecard_unauthenticated(self, client):
        res = client.get("/api/v1/workspaces/demo-workspace-01/prompts/evaluation")
        assert res.status_code == 200
        assert res.json()["scenarios_evaluated"] == 4

    def test_demo_forecast_unauthenticated(self, client):
        res = client.get("/api/v1/workspaces/demo-workspace-01/analytics/benchmark-wholesale/forecast")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert len(data["timeline"]) > 0

    def test_demo_anomalies_unauthenticated(self, client):
        res = client.get("/api/v1/workspaces/demo-workspace-01/analytics/benchmark-wholesale/anomalies")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["anomaly_count"] > 0

    def test_demo_knowledge_list_unauthenticated(self, client):
        res = client.get("/api/v1/workspaces/demo-workspace-01/knowledge/")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_demo_knowledge_search_unauthenticated(self, client):
        res = client.post(
            "/api/v1/workspaces/demo-workspace-01/knowledge/search",
            json={"query": "payment terms net 30", "top_k": 3},
        )
        assert res.status_code == 200
        data = res.json()
        assert "retrieved_chunks" in data
        assert "evidence_summary" in data

    def test_cloud_llm_requires_authentication(self, client):
        # Cloud providers must still require authentication to protect API keys
        res = client.post(
            "/api/v1/workspaces/demo-workspace-01/prompts/execute",
            json={
                "dataset_id": "benchmark-wholesale",
                "prompt_version": "v2",
                "provider_type": "openai",
            },
        )
        assert res.status_code == 401

