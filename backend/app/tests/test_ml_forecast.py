"""Tests for XGBoost Sales Forecasting Service (Stage 6).

Covers:
1. Time-series aggregation.
2. Leakage-free lag & rolling feature engineering.
3. Chronological train/test split.
4. XGBoost regressor training and evaluation metrics (MAE, RMSE, WAPE).
5. Seasonal naive baseline comparison and honest outperformance evaluation.
6. Multi-step future horizon forecasting and 95% confidence interval bounds.
7. Model artifact serialization and loading.
8. Insufficient data handling.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import joblib

from app.services.forecast_service import ForecastService

SYNTHETIC_CSV_PATH = Path(__file__).resolve().parents[3] / "data" / "samples" / "synthetic_wholesale.csv"

MAPPING = {
    "invoice_no": "InvoiceNo",
    "stock_code": "StockCode",
    "description": "Description",
    "quantity": "Quantity",
    "unit_price": "UnitPrice",
    "customer_id": "CustomerID",
    "country": "Country",
    "date": "InvoiceDate",
}


@pytest.fixture
def wholesale_df():
    """Load benchmark synthetic wholesale dataset."""
    return pd.read_csv(SYNTHETIC_CSV_PATH)


@pytest.fixture
def forecast_service_tmp(tmp_path):
    """Forecast service instance using isolated temporary models directory."""
    return ForecastService(models_dir=tmp_path)


class TestTimeSeriesAggregation:
    """Verify transaction to time-series aggregation."""

    def test_weekly_aggregation_structure(self, forecast_service_tmp, wholesale_df):
        ts_df = forecast_service_tmp.aggregate_time_series(wholesale_df, MAPPING, freq="W-MON")
        assert len(ts_df) >= 50
        assert "ds" in ts_df.columns
        assert "y" in ts_df.columns
        assert (ts_df["y"] >= 0).all()

    def test_excludes_cancellations(self, forecast_service_tmp):
        # Create small test dataset with one normal and one cancellation invoice
        test_df = pd.DataFrame([
            {"InvoiceNo": "1001", "Quantity": 10, "UnitPrice": 50.0, "InvoiceDate": "2023-01-05"},
            {"InvoiceNo": "C1002", "Quantity": -5, "UnitPrice": 50.0, "InvoiceDate": "2023-01-06"},
            {"InvoiceNo": "1003", "Quantity": 2, "UnitPrice": 100.0, "InvoiceDate": "2023-01-07"},
        ])
        mapping = {"invoice_no": "InvoiceNo", "quantity": "Quantity", "unit_price": "UnitPrice", "date": "InvoiceDate"}
        ts_df = forecast_service_tmp.aggregate_time_series(test_df, mapping, freq="W-MON")
        # Total revenue should only include 10*50 + 2*100 = 700.0 (cancellation excluded)
        assert ts_df["y"].sum() == 700.0


class TestFeatureEngineeringAndLeakagePrevention:
    """Verify feature engineering strictly prevents target leakage."""

    def test_features_shifted_prior_periods(self, forecast_service_tmp):
        # Create simple monotonically increasing series
        dates = pd.date_range("2023-01-01", periods=10, freq="W-MON")
        ts_df = pd.DataFrame({"ds": dates, "y": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]})

        feat_df = forecast_service_tmp.create_time_series_features(ts_df)

        # lag_1 for index 4 (y=50) must equal 40 (y from index 3), NOT 50
        assert feat_df.loc[4, "lag_1"] == 40
        assert feat_df.loc[4, "lag_2"] == 30
        assert feat_df.loc[4, "lag_3"] == 20
        assert feat_df.loc[4, "lag_4"] == 10

        # rolling_mean_3 for index 4 must be mean of (40, 30, 20) = 30.0
        assert feat_df.loc[4, "rolling_mean_3"] == pytest.approx(30.0, rel=1e-3)

        # Check calendar cyclical bounds
        assert (feat_df["month_sin"] >= -1.0).all() and (feat_df["month_sin"] <= 1.0).all()
        assert (feat_df["month_cos"] >= -1.0).all() and (feat_df["month_cos"] <= 1.0).all()


class TestModelTrainingAndEvaluation:
    """Verify XGBoost training, prediction, and baseline evaluation."""

    def test_train_and_forecast_success(self, forecast_service_tmp, wholesale_df):
        resp = forecast_service_tmp.train_and_forecast(
            dataset_id="test_wholesale",
            dataset_name="Synthetic Wholesale",
            df=wholesale_df,
            mapping=MAPPING,
            forecast_horizon=6,
            freq="W-MON"
        )

        assert resp.status == "success"
        assert resp.historical_periods_count >= 50
        assert resp.forecast_horizon_periods == 6
        assert len(resp.timeline) > resp.historical_periods_count

        # Check evaluation summary
        assert resp.evaluation is not None
        assert resp.evaluation.xgboost_metrics.wape >= 0.0
        assert resp.evaluation.xgboost_metrics.mae >= 0.0
        assert resp.evaluation.xgboost_metrics.rmse >= 0.0
        assert resp.evaluation.baseline_metrics.wape >= 0.0
        assert isinstance(resp.evaluation.outperforms_baseline, bool)
        assert len(resp.evaluation.evaluation_verdict) > 10

        # Check feature importances
        assert len(resp.feature_importances) > 0
        assert resp.feature_importances[0].importance_score >= 0.0

    def test_future_forecast_confidence_bounds(self, forecast_service_tmp, wholesale_df):
        resp = forecast_service_tmp.train_and_forecast(
            dataset_id="test_wholesale_bounds",
            dataset_name="Synthetic Wholesale",
            df=wholesale_df,
            mapping=MAPPING,
            forecast_horizon=6,
            freq="W-MON"
        )

        future_points = [p for p in resp.timeline if p.is_forecast]
        assert len(future_points) == 6

        for pt in future_points:
            assert pt.forecast is not None
            assert pt.lower_bound is not None
            assert pt.upper_bound is not None
            # Lower bound <= Forecast <= Upper bound
            assert pt.lower_bound <= pt.forecast <= pt.upper_bound
            assert pt.lower_bound >= 0.0  # Revenue cannot be negative

    def test_wape_calculation_edge_cases(self, forecast_service_tmp):
        # Perfect predictions: WAPE = 0.0
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([100.0, 200.0, 300.0])
        assert forecast_service_tmp.calculate_wape(y_true, y_pred) == 0.0

        # 10% consistent error: WAPE = 10.0
        y_pred_10 = np.array([110.0, 220.0, 330.0])
        assert forecast_service_tmp.calculate_wape(y_true, y_pred_10) == pytest.approx(10.0, rel=1e-3)


class TestModelArtifactsAndEdgeCases:
    """Verify model persistence and data sufficiency guards."""

    def test_model_artifact_saved(self, forecast_service_tmp, wholesale_df):
        resp = forecast_service_tmp.train_and_forecast(
            dataset_id="persist_test",
            dataset_name="Synthetic Wholesale",
            df=wholesale_df,
            mapping=MAPPING,
            forecast_horizon=4
        )
        assert resp.status == "success"

        # Check that joblib file exists
        saved_file = forecast_service_tmp._get_model_path("persist_test")
        assert saved_file.exists()

        # Reload and check contents
        loaded = joblib.load(saved_file)
        assert "model" in loaded
        assert "feature_cols" in loaded
        assert "trained_at" in loaded

    def test_insufficient_data_refusal(self, forecast_service_tmp):
        # Only 3 weeks of data (below minimum threshold of 10)
        short_df = pd.DataFrame([
            {"InvoiceNo": "1", "Quantity": 5, "UnitPrice": 10.0, "InvoiceDate": "2023-01-01"},
            {"InvoiceNo": "2", "Quantity": 8, "UnitPrice": 10.0, "InvoiceDate": "2023-01-08"},
            {"InvoiceNo": "3", "Quantity": 4, "UnitPrice": 10.0, "InvoiceDate": "2023-01-15"},
        ])
        resp = forecast_service_tmp.train_and_forecast(
            dataset_id="short_dataset",
            dataset_name="Short Data",
            df=short_df,
            mapping=MAPPING,
            forecast_horizon=4
        )
        assert resp.status == "insufficient_data"
        assert "Insufficient historical data" in resp.message
