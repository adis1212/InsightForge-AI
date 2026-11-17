"""Pydantic schemas for Machine Learning Intelligence (Stage 6).

Covers:
1. XGBoost Sales Forecasting schemas (Historical, Multi-step Forecast, Naive Baseline, Evaluation Metrics).
2. Isolation Forest Anomaly Detection schemas (Score distribution, Flagged Records, Pattern Tags).
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ==========================================
# 1. XGBoost Sales Forecasting Schemas
# ==========================================

class ForecastDataPoint(BaseModel):
    """Single period observation or forecast point."""
    period: str = Field(..., description="Time period identifier (e.g. '2023-W24' or '2023-06')")
    actual: Optional[float] = Field(None, description="Actual observed revenue (None for future forecast periods)")
    forecast: Optional[float] = Field(None, description="XGBoost predicted revenue")
    lower_bound: Optional[float] = Field(None, description="Lower 95% confidence bound")
    upper_bound: Optional[float] = Field(None, description="Upper 95% confidence bound")
    baseline_forecast: Optional[float] = Field(None, description="Seasonal/Lag naive benchmark forecast")
    is_forecast: bool = Field(False, description="True if period is in the future horizon")


class ForecastMetrics(BaseModel):
    """Evaluation metrics computed strictly on chronological holdout test set."""
    mae: float = Field(..., description="Mean Absolute Error in currency units")
    rmse: float = Field(..., description="Root Mean Squared Error in currency units")
    wape: float = Field(..., description="Weighted Absolute Percentage Error (sum(|y-y_hat|) / sum(y) * 100)")
    test_periods_count: int = Field(..., description="Number of holdout test periods evaluated")


class ModelEvaluationSummary(BaseModel):
    """Comparison between XGBoost model and seasonal naive baseline."""
    xgboost_metrics: ForecastMetrics
    baseline_metrics: ForecastMetrics
    outperforms_baseline: bool = Field(..., description="True if XGBoost WAPE < Baseline WAPE")
    wape_improvement_pct: float = Field(..., description="Percentage improvement in WAPE over baseline")
    rmse_improvement_pct: float = Field(..., description="Percentage improvement in RMSE over baseline")
    evaluation_verdict: str = Field(..., description="Evidence-backed verdict on model commercial utility")


class FeatureImportance(BaseModel):
    """Relative importance of time-series features in XGBoost regressor."""
    feature_name: str
    importance_score: float = Field(..., description="Gain or weight importance score normalized to [0, 1]")


class ForecastResponse(BaseModel):
    """Complete response payload for XGBoost revenue forecasting."""
    dataset_id: str
    dataset_name: str
    status: Literal["success", "insufficient_data", "error"]
    message: str
    frequency: str = Field("weekly", description="Time aggregation frequency ('weekly' or 'monthly')")
    historical_periods_count: int
    forecast_horizon_periods: int
    timeline: list[ForecastDataPoint]
    evaluation: Optional[ModelEvaluationSummary] = None
    feature_importances: list[FeatureImportance] = Field(default_factory=list)
    model_metadata: dict = Field(default_factory=dict)
    methodological_notes: list[str] = Field(default_factory=list)


# ==========================================
# 2. Isolation Forest Anomaly Schemas
# ==========================================

class AnomalyRecord(BaseModel):
    """Detailed record for an individual flagged transaction outlier."""
    invoice_no: str
    stock_code: str
    description: str
    quantity: float
    unit_price: float
    total_amount: float
    invoice_date: str
    customer_id: str
    country: str
    anomaly_score: float = Field(..., description="Normalized anomaly score in [0, 1], higher is more anomalous")
    risk_severity: Literal["critical", "high", "medium", "low"]
    suspicious_reasons: list[str] = Field(..., description="Explainable pattern tags (e.g. 'EXTREME_UNIT_PRICE')")


class AnomalyDistributionBucket(BaseModel):
    """Histogram bucket for anomaly score distribution."""
    score_range: str
    count: int
    is_anomaly_zone: bool


class AnomalyResponse(BaseModel):
    """Complete response payload for Isolation Forest anomaly detection."""
    dataset_id: str
    dataset_name: str
    status: Literal["success", "insufficient_data", "error"]
    message: str
    total_records_analyzed: int
    anomaly_count: int
    contamination_rate: float
    score_threshold: float
    severity_breakdown: dict[str, int]
    distribution_buckets: list[AnomalyDistributionBucket]
    flagged_anomalies: list[AnomalyRecord]
    model_metadata: dict = Field(default_factory=dict)
    disclaimer: str = Field(
        "Statistical anomaly detection flags mathematically unusual transactions based on isolation trees. "
        "Flags represent statistical deviation, NOT confirmed fraudulent activity or operational errors."
    )
