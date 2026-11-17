"""API endpoints for the Evidence-Grounded Prompt Engineering Engine."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Literal
from pydantic import BaseModel, Field
import os
import json
from pathlib import Path

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.dataset import Dataset
from app.schemas.prompt_schemas import (
    PromptChainExecutionResponse, PromptComparisonResponse,
    EvaluationBenchmarkScorecard
)
from app.services.prompt_service import prompt_service
from app.services.analytics_service import AnalyticsService
from app.services.dataset_service import read_dataset
from app.services.retrieval_service import retrieval_service
from scripts.evaluate_prompts import run_evaluation, GOLDEN_SCENARIOS

router = APIRouter(prefix="/workspaces/{workspace_id}/prompts", tags=["Prompt Engineering"])

PROMPTS_DIR = Path(__file__).resolve().parents[3] / "prompts"


class ExecutePromptRequest(BaseModel):
    """Request to execute a prompt chain on a dataset."""
    dataset_id: str
    prompt_version: Literal["v1", "v2"] = "v2"
    provider_type: Optional[str] = "local_demo"
    rag_query: Optional[str] = None


class ComparePromptsRequest(BaseModel):
    """Request to compare v1 and v2 side-by-side on identical dataset KPIs."""
    dataset_id: str
    provider_type: Optional[str] = "local_demo"
    rag_query: Optional[str] = None


def _check_workspace_access(db: Session, workspace_id: str, user: Optional[User]):
    """Verify workspace membership, permitting demo workspace access."""
    if workspace_id.startswith("demo-"):
        return None
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")
    return member


def _get_dataset_kpis(db: Session, workspace_id: str, dataset_id: str) -> tuple[str, dict]:
    """Helper to load dataset and calculate deterministic Pandas KPIs."""
    if dataset_id.startswith("demo-") or dataset_id == "benchmark-wholesale":
        # Fallback to golden scenario 1 for demo dataset
        scn = GOLDEN_SCENARIOS[0]
        kpi_dict = dict(scn["kpis"])
        kpi_dict["ml_forecast"] = {
            "wape": 23.9,
            "outperforms_baseline": False,
            "forecast_horizon_periods": 6,
        }
        kpi_dict["ml_anomalies"] = {
            "anomaly_count": 151,
            "critical_count": 20,
            "contamination_rate": 0.03,
        }
        return scn["dataset_name"], kpi_dict

    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    if not dataset.column_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column mapping required before running prompt chains.",
        )

    df = read_dataset(dataset.file_path)
    analytics = AnalyticsService(df, dataset.column_mapping)
    summary = analytics.calculate_summary(dataset_id)
    top_prods = analytics.calculate_top_products(limit=1)
    geos = analytics.calculate_geographic_performance()

    kpi_dict = {
        "total_revenue": summary.total_revenue.value or 0.0,
        "unique_orders": summary.unique_orders.value or 0,
        "units_sold": summary.units_sold.value or 0,
        "average_order_value": summary.average_order_value.value or 0.0,
        "unique_customers": summary.unique_customers.value or 0,
        "cancellation_rate": summary.cancellation_rate.value or 0.0,
        "top_product": top_prods[0].description if top_prods else "Primary SKU",
        "top_product_revenue": top_prods[0].total_revenue if top_prods else 0.0,
        "top_country": geos[0].country if geos else "Primary Market",
        "top_country_revenue": geos[0].revenue if geos else 0.0,
    }
    return dataset.name, kpi_dict


@router.post("/execute", response_model=PromptChainExecutionResponse)
def execute_prompt_chain(
    workspace_id: str,
    payload: ExecutePromptRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Execute the 3-stage Evidence-Grounded Prompt Chain:
    Stage 1: Factual Data Summarization (Jinja2 -> claims)
    Stage 2: Strategic Insights & Hypotheses (Jinja2 -> risks/recommendations)
    Stage 3: Structured Executive Report (Jinja2 -> Pydantic JSON)
    """
    _check_workspace_access(db, workspace_id, current_user)

    if payload.provider_type and payload.provider_type != "local_demo" and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to invoke cloud LLM providers.",
        )

    dataset_name, kpi_data = _get_dataset_kpis(db, workspace_id, payload.dataset_id)

    # Retrieve grounded business document evidence from workspace knowledge base
    rag_query = payload.rag_query or f"payment terms cancellation return policy contract SLAs for {dataset_name}"
    rag_evidence = retrieval_service.retrieve(
        db=db,
        workspace_id=workspace_id,
        query=rag_query,
        top_k=3,
    )

    return prompt_service.execute_chain(
        dataset_id=payload.dataset_id,
        dataset_name=dataset_name,
        kpi_data=kpi_data,
        prompt_version=payload.prompt_version,
        provider_type=payload.provider_type,
        rag_evidence=rag_evidence,
    )


@router.post("/compare", response_model=PromptComparisonResponse)
def compare_prompt_versions(
    workspace_id: str,
    payload: ComparePromptsRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Execute both Prompt v1 (baseline) and Prompt v2 (grounded) side-by-side
    on identical test data to measure accuracy delta, hallucination reduction,
    and schema compliance.
    """
    _check_workspace_access(db, workspace_id, current_user)

    if payload.provider_type and payload.provider_type != "local_demo" and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to invoke cloud LLM providers.",
        )

    dataset_name, kpi_data = _get_dataset_kpis(db, workspace_id, payload.dataset_id)

    # Retrieve grounded business document evidence from workspace knowledge base
    rag_query = payload.rag_query or f"payment terms cancellation return policy contract SLAs for {dataset_name}"
    rag_evidence = retrieval_service.retrieve(
        db=db,
        workspace_id=workspace_id,
        query=rag_query,
        top_k=3,
    )

    return prompt_service.compare_versions(
        dataset_id=payload.dataset_id,
        dataset_name=dataset_name,
        kpi_data=kpi_data,
        provider_type=payload.provider_type,
        rag_evidence=rag_evidence,
    )


@router.get("/templates")
def list_prompt_templates(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Inspect stored Jinja2 prompt templates and documented differences between v1 and v2."""
    _check_workspace_access(db, workspace_id, current_user)

    templates = {}
    for filename in sorted(os.listdir(PROMPTS_DIR)):
        if filename.endswith(".jinja2"):
            path = PROMPTS_DIR / filename
            templates[filename] = path.read_text(encoding="utf-8")

    return {
        "templates": templates,
        "version_differences": {
            "Prompt 1": "v1 uses unconstrained prose vulnerable to loose approximations. v2 requires strict structured claims with [METRIC:id] citations.",
            "Prompt 2": "v1 generates general speculation. v2 mandates explicit [HYPOTHESIS] prefixes and requires 'Insufficient data' for unsupported causal factors.",
            "Prompt 3": "v1 frequently outputs conversational markdown. v2 enforces pure JSON strictly matching the ExecutiveCommercialReport Pydantic schema."
        }
    }


@router.get("/evaluation", response_model=EvaluationBenchmarkScorecard)
def get_evaluation_scorecard(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Retrieve the latest automated evaluation scorecard comparing v1 vs v2 across golden datasets."""
    _check_workspace_access(db, workspace_id, current_user)

    scorecard_file = Path(__file__).resolve().parents[5] / "data" / "samples" / "latest_evaluation_scorecard.json"
    if scorecard_file.exists():
        with open(scorecard_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return EvaluationBenchmarkScorecard.model_validate(data)

    # Run on demand if not present
    return run_evaluation()


@router.post("/evaluate", response_model=EvaluationBenchmarkScorecard)
def trigger_evaluation(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Trigger a fresh automated evaluation across all golden benchmark scenarios."""
    _check_workspace_access(db, workspace_id, current_user)
    return run_evaluation()
