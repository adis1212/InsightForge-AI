"""Analytics API endpoints."""
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.dataset import Dataset
from app.schemas.analytics import AnalyticsResponse, KPISummary
from app.schemas.ml_schemas import ForecastResponse, AnomalyResponse
from app.services.analytics_service import AnalyticsService
from app.services.dataset_service import read_dataset
from app.services.future_services import forecast_service, anomaly_service

router = APIRouter(prefix="/workspaces/{workspace_id}/analytics", tags=["Analytics"])

SYNTHETIC_DATASET_PATH = Path(__file__).resolve().parents[5] / "data" / "samples" / "synthetic_wholesale.csv"
BHARATTRADE_DATASET_PATH = Path(__file__).resolve().parents[5] / "data" / "samples" / "bharattrade_fmcg_transactions.csv"

SYNTHETIC_MAPPING = {
    "invoice_no": "InvoiceNo",
    "stock_code": "StockCode",
    "description": "Description",
    "quantity": "Quantity",
    "unit_price": "UnitPrice",
    "customer_id": "CustomerID",
    "country": "Country",
    "date": "InvoiceDate",
}

BHARATTRADE_MAPPING = {
    "invoice_no": "InvoiceNo",
    "stock_code": "StockCode",
    "description": "Description",
    "quantity": "Quantity",
    "unit_price": "UnitPrice",
    "customer_id": "CustomerID",
    "country": "State",
    "date": "InvoiceDate",
    "category": "Category",
    "unit_cost": "UnitCost",
    "city": "City",
}


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


def _get_dataset_or_demo(db: Session, workspace_id: str, dataset_id: str):
    """Get dataset object or return synthetic demo dataset parameters."""
    if dataset_id.startswith("demo-") or dataset_id == "benchmark-wholesale":
        if not SYNTHETIC_DATASET_PATH.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Synthetic benchmark dataset file not found")
        df = read_dataset(str(SYNTHETIC_DATASET_PATH))
        return df, SYNTHETIC_MAPPING

    if dataset_id == "bharattrade-demo" or dataset_id.startswith("bharattrade"):
        if not BHARATTRADE_DATASET_PATH.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BharatTrade Indian demo dataset file not found")
        df = read_dataset(str(BHARATTRADE_DATASET_PATH))
        return df, BHARATTRADE_MAPPING

    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    if dataset.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset is not ready for analysis (status: {dataset.status})",
        )
    if not dataset.column_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column mapping not configured. Upload or map columns first.",
        )
    df = read_dataset(dataset.file_path)
    return df, dataset.column_mapping


def _detect_currency(dataset_id: str) -> str:
    """Detect currency based on dataset ID."""
    if dataset_id.startswith("bharattrade"):
        return "INR"
    return "USD"


@router.get("/{dataset_id}", response_model=AnalyticsResponse)
def get_analytics(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get full analytics for a dataset (deterministic Pandas calculations)."""
    _check_workspace_access(db, workspace_id, current_user)
    df, mapping = _get_dataset_or_demo(db, workspace_id, dataset_id)
    currency = _detect_currency(dataset_id)
    service = AnalyticsService(df, mapping, currency=currency)
    return service.calculate_full_analytics(dataset_id)


@router.get("/{dataset_id}/summary", response_model=KPISummary)
def get_kpi_summary(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get KPI summary for a dataset."""
    _check_workspace_access(db, workspace_id, current_user)
    df, mapping = _get_dataset_or_demo(db, workspace_id, dataset_id)
    currency = _detect_currency(dataset_id)
    service = AnalyticsService(df, mapping, currency=currency)
    return service.calculate_summary(dataset_id)


@router.get("/{dataset_id}/forecast", response_model=ForecastResponse)
def get_forecast(
    workspace_id: str,
    dataset_id: str,
    periods: int = 6,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get XGBoost sales forecast with naive baseline comparison and 95% confidence bounds."""
    _check_workspace_access(db, workspace_id, current_user)
    df, mapping = _get_dataset_or_demo(db, workspace_id, dataset_id)
    dataset_name = "Wholesale Benchmark (FY2023)" if dataset_id.startswith("demo-") or dataset_id == "benchmark-wholesale" else ("BharatTrade Distributors (FY2023-24)" if dataset_id.startswith("bharattrade") else dataset_id)
    return forecast_service.predict(
        dataset_id=dataset_id,
        periods=periods,
        df=df,
        mapping=mapping,
        dataset_name=dataset_name,
    )


@router.get("/{dataset_id}/anomalies", response_model=AnomalyResponse)
def get_anomalies(
    workspace_id: str,
    dataset_id: str,
    contamination: float = 0.03,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Detect transaction outliers using Isolation Forest with explainable pattern tags."""
    _check_workspace_access(db, workspace_id, current_user)
    df, mapping = _get_dataset_or_demo(db, workspace_id, dataset_id)
    dataset_name = "Wholesale Benchmark (FY2023)" if dataset_id.startswith("demo-") or dataset_id == "benchmark-wholesale" else ("BharatTrade Distributors (FY2023-24)" if dataset_id.startswith("bharattrade") else dataset_id)
    return anomaly_service.detect(
        dataset_id=dataset_id,
        df=df,
        mapping=mapping,
        dataset_name=dataset_name,
        contamination=contamination,
    )
