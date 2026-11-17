"""XGBoost Sales Forecasting Service (Stage 6).

Implements:
1. Historical sales aggregation (daily/weekly/monthly).
2. Leakage-free time-series feature engineering (lags, rolling stats, calendar cyclical features).
3. Chronological train/test split.
4. XGBoost regressor training and hyperparameter configuration.
5. Seasonal naive baseline benchmark comparison.
6. Empirical evaluation metrics (MAE, RMSE, WAPE).
7. Multi-step recursive future horizon forecast with 95% confidence intervals.
8. Model artifact persistence using joblib.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Optional, Any
from datetime import datetime, timezone
import joblib
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.schemas.ml_schemas import (
    ForecastResponse, ForecastDataPoint, ForecastMetrics,
    ModelEvaluationSummary, FeatureImportance
)

MODELS_DIR = Path(__file__).resolve().parents[3] / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class ForecastService:
    """Production XGBoost time-series revenue forecasting engine."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR

    def _get_model_path(self, dataset_id: str) -> Path:
        clean_id = dataset_id.replace("/", "_").replace("\\", "_")
        return self.models_dir / f"xgb_forecast_{clean_id}.joblib"

    def aggregate_time_series(
        self,
        df: pd.DataFrame,
        mapping: dict[str, str],
        freq: str = "W-MON"
    ) -> pd.DataFrame:
        """
        Aggregate transaction logs into a continuous regular time series.
        Excludes cancelled invoices and calculates net revenue per period.
        """
        date_col = mapping.get("date", "InvoiceDate")
        qty_col = mapping.get("quantity", "Quantity")
        price_col = mapping.get("unit_price", "UnitPrice")
        inv_col = mapping.get("invoice_no", "InvoiceNo")

        work_df = df.copy()

        # Filter out cancellations for standard net sales forecasting
        if inv_col in work_df.columns:
            work_df = work_df[~work_df[inv_col].astype(str).str.startswith("C", na=False)]
        if qty_col in work_df.columns:
            work_df = work_df[work_df[qty_col] > 0]

        # Parse dates
        work_df[date_col] = pd.to_datetime(work_df[date_col], errors="coerce")
        work_df = work_df.dropna(subset=[date_col])

        # Compute line revenue
        work_df["line_revenue"] = work_df[qty_col] * work_df[price_col]

        # Sort and resample
        work_df = work_df.sort_values(date_col)
        ts_df = (
            work_df.set_index(date_col)
            .resample(freq)["line_revenue"]
            .sum()
            .reset_index()
            .rename(columns={date_col: "ds", "line_revenue": "y"})
        )

        return ts_df

    def create_time_series_features(self, ts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create strictly prior-shifted lag and rolling features to prevent leakage.
        No current period (y_t) information is included in features at time t.
        """
        df = ts_df.copy().sort_values("ds").reset_index(drop=True)

        # Prior-period lags
        df["lag_1"] = df["y"].shift(1)
        df["lag_2"] = df["y"].shift(2)
        df["lag_3"] = df["y"].shift(3)
        df["lag_4"] = df["y"].shift(4)

        # Rolling statistics strictly on shifted data (t-1, t-2, t-3)
        df["rolling_mean_3"] = df["y"].shift(1).rolling(window=3, min_periods=2).mean()
        df["rolling_std_3"] = df["y"].shift(1).rolling(window=3, min_periods=2).std().fillna(0.0)
        df["rolling_mean_6"] = df["y"].shift(1).rolling(window=6, min_periods=3).mean()

        # Calendar and cyclical features
        df["month"] = df["ds"].dt.month
        df["quarter"] = df["ds"].dt.quarter
        df["week_of_year"] = df["ds"].dt.isocalendar().week.astype(int)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)
        df["trend_index"] = np.arange(len(df))

        return df

    def calculate_wape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Weighted Absolute Percentage Error = sum(|y - y_hat|) / sum(y) * 100."""
        denom = np.sum(np.abs(y_true))
        if denom < 1e-6:
            return 0.0
        return float(np.sum(np.abs(y_true - y_pred)) / denom * 100.0)

    def train_and_forecast(
        self,
        dataset_id: str,
        dataset_name: str,
        df: pd.DataFrame,
        mapping: dict[str, str],
        forecast_horizon: int = 6,
        freq: str = "W-MON"
    ) -> ForecastResponse:
        """
        Train XGBoost on historical sales series, evaluate against Naive Baseline,
        and project multi-step future sales with confidence bounds.
        """
        ts_df = self.aggregate_time_series(df, mapping, freq=freq)

        # Check data sufficiency: Need at least 10 periods
        if len(ts_df) < 10:
            return ForecastResponse(
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                status="insufficient_data",
                message=f"Insufficient historical data: {len(ts_df)} periods available (minimum 10 required for XGBoost).",
                frequency="weekly" if "W" in freq else "monthly",
                historical_periods_count=len(ts_df),
                forecast_horizon_periods=forecast_horizon,
                timeline=[
                    ForecastDataPoint(
                        period=row["ds"].strftime("%Y-W%U" if "W" in freq else "%Y-%m"),
                        actual=round(float(row["y"]), 2),
                        is_forecast=False
                    )
                    for _, row in ts_df.iterrows()
                ],
                methodological_notes=["Data did not meet the minimum 10-period threshold for reliable time-series modeling."]
            )

        # Feature engineering
        feat_df = self.create_time_series_features(ts_df)

        feature_cols = [
            "lag_1", "lag_2", "lag_3", "lag_4",
            "rolling_mean_3", "rolling_std_3", "rolling_mean_6",
            "month", "quarter", "month_sin", "month_cos", "trend_index"
        ]

        # Drop initial rows where lags are undefined
        valid_df = feat_df.dropna(subset=["lag_4", "rolling_mean_3"]).reset_index(drop=True)

        if len(valid_df) < 6:
            return ForecastResponse(
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                status="insufficient_data",
                message="Dataset has insufficient time steps after lag feature construction.",
                frequency="weekly" if "W" in freq else "monthly",
                historical_periods_count=len(ts_df),
                forecast_horizon_periods=forecast_horizon,
                timeline=[]
            )

        # Chronological train/test split (Holdout testing)
        test_size = max(3, int(len(valid_df) * 0.20))
        train_df = valid_df.iloc[:-test_size].copy()
        test_df = valid_df.iloc[-test_size:].copy()

        X_train, y_train = train_df[feature_cols], train_df["y"].values
        X_test, y_test = test_df[feature_cols], test_df["y"].values

        # Train XGBoost regressor with controlled regularization
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            objective="reg:squarederror"
        )
        model.fit(X_train, y_train)

        # Save model artifact
        model_path = self._get_model_path(dataset_id)
        joblib.dump({"model": model, "feature_cols": feature_cols, "trained_at": datetime.now(timezone.utc).isoformat()}, model_path)

        # Model evaluation on chronological test set
        y_pred_test = np.maximum(model.predict(X_test), 0.0)

        # Baseline: Seasonal Naive / Lag-1 Persistence (y_t = y_{t-1})
        y_pred_baseline = test_df["lag_1"].values

        # Compute empirical metrics
        xgb_mae = float(mean_absolute_error(y_test, y_pred_test))
        xgb_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
        xgb_wape = float(self.calculate_wape(y_test, y_pred_test))

        base_mae = float(mean_absolute_error(y_test, y_pred_baseline))
        base_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_baseline)))
        base_wape = float(self.calculate_wape(y_test, y_pred_baseline))

        outperforms = xgb_wape < base_wape
        wape_improvement = round(((base_wape - xgb_wape) / (base_wape + 1e-6)) * 100, 2)
        rmse_improvement = round(((base_rmse - xgb_rmse) / (base_rmse + 1e-6)) * 100, 2)

        if outperforms:
            verdict = (
                f"XGBoost outperforms the seasonal naive baseline on this dataset with a WAPE of {xgb_wape:.1f}% "
                f"({wape_improvement:+.1f}% error reduction over baseline {base_wape:.1f}%)."
            )
        else:
            verdict = (
                f"XGBoost WAPE is {xgb_wape:.1f}% vs. baseline {base_wape:.1f}%. The naive baseline remains competitive; "
                f"additional historical transaction seasonality is recommended before deploying pure ML."
            )

        evaluation = ModelEvaluationSummary(
            xgboost_metrics=ForecastMetrics(
                mae=round(xgb_mae, 2),
                rmse=round(xgb_rmse, 2),
                wape=round(xgb_wape, 2),
                test_periods_count=test_size
            ),
            baseline_metrics=ForecastMetrics(
                mae=round(base_mae, 2),
                rmse=round(base_rmse, 2),
                wape=round(base_wape, 2),
                test_periods_count=test_size
            ),
            outperforms_baseline=outperforms,
            wape_improvement_pct=wape_improvement,
            rmse_improvement_pct=rmse_improvement,
            evaluation_verdict=verdict
        )

        # Feature importances
        importances = model.feature_importances_
        feature_importance_list = [
            FeatureImportance(
                feature_name=col,
                importance_score=round(float(score), 4)
            )
            for col, score in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
        ]

        # Multi-step future recursive forecasting
        current_history = ts_df.copy()
        last_date = current_history["ds"].iloc[-1]
        freq_offset = pd.tseries.frequencies.to_offset(freq)

        future_rows = []
        residual_std = float(np.std(y_test - y_pred_test)) if len(y_test) > 1 else (xgb_mae * 1.25)
        residual_std = max(residual_std, 100.0)

        for step in range(1, forecast_horizon + 1):
            next_date = last_date + (freq_offset * step)
            # Recompute features on updated history
            temp_feat = self.create_time_series_features(current_history)
            latest_features = temp_feat.iloc[[-1]][feature_cols]

            next_pred = float(np.maximum(model.predict(latest_features)[0], 0.0))

            # Residual-based 95% confidence interval (expands with horizon step)
            conf_margin = 1.96 * residual_std * np.sqrt(step)
            lower_bound = float(np.maximum(next_pred - conf_margin, 0.0))
            upper_bound = float(next_pred + conf_margin)

            future_rows.append({
                "ds": next_date,
                "y": next_pred,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            })

            # Append prediction to history for next recursive step
            current_history = pd.concat([
                current_history,
                pd.DataFrame([{"ds": next_date, "y": next_pred}])
            ], ignore_index=True)

        # Assemble full timeline (Historical Actuals + Test Fit + Future Forecasts)
        timeline: list[ForecastDataPoint] = []

        # Training points (actuals only)
        for _, row in train_df.iterrows():
            p_str = row["ds"].strftime("%Y-W%U" if "W" in freq else "%Y-%m")
            timeline.append(ForecastDataPoint(
                period=p_str,
                actual=round(float(row["y"]), 2),
                forecast=None,
                baseline_forecast=None,
                is_forecast=False
            ))

        # Test points (actuals + test predictions + baseline)
        for i, row in test_df.reset_index(drop=True).iterrows():
            p_str = row["ds"].strftime("%Y-W%U" if "W" in freq else "%Y-%m")
            timeline.append(ForecastDataPoint(
                period=p_str,
                actual=round(float(row["y"]), 2),
                forecast=round(float(y_pred_test[i]), 2),
                baseline_forecast=round(float(y_pred_baseline[i]), 2),
                lower_bound=round(float(np.maximum(y_pred_test[i] - 1.96 * residual_std, 0.0)), 2),
                upper_bound=round(float(y_pred_test[i] + 1.96 * residual_std), 2),
                is_forecast=False
            ))

        # Future forecast points
        for row in future_rows:
            p_str = row["ds"].strftime("%Y-W%U" if "W" in freq else "%Y-%m")
            timeline.append(ForecastDataPoint(
                period=p_str,
                actual=None,
                forecast=round(float(row["y"]), 2),
                lower_bound=round(float(row["lower_bound"]), 2),
                upper_bound=round(float(row["upper_bound"]), 2),
                baseline_forecast=round(float(ts_df["y"].iloc[-1]), 2),
                is_forecast=True
            ))

        return ForecastResponse(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            status="success",
            message=f"XGBoost forecast completed successfully for {forecast_horizon} periods.",
            frequency="weekly" if "W" in freq else "monthly",
            historical_periods_count=len(ts_df),
            forecast_horizon_periods=forecast_horizon,
            timeline=timeline,
            evaluation=evaluation,
            feature_importances=feature_importance_list,
            model_metadata={
                "model_name": "XGBoost Regressor (Tree-based Gradient Boosting)",
                "n_estimators": 100,
                "max_depth": 3,
                "learning_rate": 0.08,
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "artifact_saved": str(model_path.name)
            },
            methodological_notes=[
                "Chronological holdout split: The final 20% of periods were held out for strict out-of-sample evaluation.",
                "Zero data leakage: All rolling and lag features are computed with a 1-period forward shift.",
                "Confidence bounds: 95% interval derived from holdout residual variance scaling with sqrt(horizon)."
            ]
        )

    def predict(
        self,
        dataset_id: str,
        periods: int = 6,
        df: Optional[pd.DataFrame] = None,
        mapping: Optional[dict[str, str]] = None,
        dataset_name: str = "Active Dataset"
    ) -> ForecastResponse:
        """API wrapper for predicting revenue."""
        if df is None or mapping is None:
            return ForecastResponse(
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                status="error",
                message="DataFrame and column mapping required for forecast training.",
                frequency="weekly",
                historical_periods_count=0,
                forecast_horizon_periods=periods,
                timeline=[]
            )

        return self.train_and_forecast(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            df=df,
            mapping=mapping,
            forecast_horizon=periods
        )


# Global singleton instance
forecast_service = ForecastService()
