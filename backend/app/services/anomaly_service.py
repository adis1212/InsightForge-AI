"""Isolation Forest Anomaly Detection Service (Stage 6).

Implements:
1. Transaction-level feature engineering (SKU median deviations, cancellation flags, temporal hour flags).
2. Isolation Forest unsupervised model training.
3. Normalized continuous anomaly scoring in [0, 1].
4. Explainable suspicious-pattern categorization (EXTREME_PRICE, BULK_QUANTITY, CANCELLATION_SPIKE, etc.).
5. Risk severity tiering (CRITICAL, HIGH, MEDIUM, LOW).
6. Preserved source record references (InvoiceNo, StockCode, CustomerID, Description).
7. Score distribution histogram calculation for dashboard charts.
8. Model persistence and synthetic anomaly validation capabilities.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Optional, Any
from datetime import datetime, timezone
import joblib
from sklearn.ensemble import IsolationForest

from app.schemas.ml_schemas import (
    AnomalyResponse, AnomalyRecord, AnomalyDistributionBucket
)

MODELS_DIR = Path(__file__).resolve().parents[3] / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class AnomalyService:
    """Production Isolation Forest transaction outlier detection engine."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR

    def _get_model_path(self, dataset_id: str) -> Path:
        clean_id = dataset_id.replace("/", "_").replace("\\", "_")
        return self.models_dir / f"iso_forest_{clean_id}.joblib"

    def extract_features(
        self,
        df: pd.DataFrame,
        mapping: dict[str, str]
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        """
        Extract numerical and behavioral features for every transaction line item.
        Computes deviations from SKU medians and off-hour flags.
        """
        date_col = mapping.get("date", "InvoiceDate")
        qty_col = mapping.get("quantity", "Quantity")
        price_col = mapping.get("unit_price", "UnitPrice")
        inv_col = mapping.get("invoice_no", "InvoiceNo")
        sku_col = mapping.get("stock_code", "StockCode")
        desc_col = mapping.get("description", "Description")
        cust_col = mapping.get("customer_id", "CustomerID")
        country_col = mapping.get("country", "Country")

        work_df = df.copy()

        # Fill missing values for text fields
        work_df[sku_col] = work_df[sku_col].fillna("UNKNOWN_SKU").astype(str)
        work_df[desc_col] = work_df[desc_col].fillna("No Description").astype(str)
        work_df[cust_col] = work_df[cust_col].fillna("GUEST").astype(str)
        work_df[country_col] = work_df[country_col].fillna("Unknown").astype(str)
        work_df[inv_col] = work_df[inv_col].fillna("000000").astype(str)

        # Ensure numeric fields
        work_df[qty_col] = pd.to_numeric(work_df[qty_col], errors="coerce").fillna(0.0)
        work_df[price_col] = pd.to_numeric(work_df[price_col], errors="coerce").fillna(0.0)

        # Basic transaction features
        work_df["total_amount"] = work_df[qty_col] * work_df[price_col]
        work_df["abs_quantity"] = np.abs(work_df[qty_col])
        work_df["is_cancellation"] = (
            work_df[inv_col].str.startswith("C", na=False) | (work_df[qty_col] < 0)
        ).astype(int)

        # SKU-level medians for price and quantity
        sku_medians = work_df.groupby(sku_col).agg(
            sku_median_price=(price_col, "median"),
            sku_median_qty=("abs_quantity", "median")
        ).reset_index()

        work_df = work_df.merge(sku_medians, on=sku_col, how="left")
        work_df["sku_median_price"] = work_df["sku_median_price"].fillna(work_df[price_col].median() or 1.0)
        work_df["sku_median_qty"] = work_df["sku_median_qty"].fillna(work_df["abs_quantity"].median() or 1.0)

        # Relative deviations from SKU medians
        work_df["price_ratio"] = work_df[price_col] / (work_df["sku_median_price"] + 1e-4)
        work_df["qty_ratio"] = work_df["abs_quantity"] / (work_df["sku_median_qty"] + 1e-4)
        work_df["log_amount"] = np.log1p(np.maximum(np.abs(work_df["total_amount"]), 0.0))

        # Temporal features
        dt_series = pd.to_datetime(work_df[date_col], errors="coerce")
        work_df["parsed_hour"] = dt_series.dt.hour.fillna(12).astype(int)
        work_df["parsed_dayofweek"] = dt_series.dt.dayofweek.fillna(2).astype(int)
        work_df["is_off_hours"] = ((work_df["parsed_hour"] < 7) | (work_df["parsed_hour"] > 19)).astype(int)
        work_df["is_weekend"] = work_df["parsed_dayofweek"].isin([5, 6]).astype(int)

        feature_cols = [
            price_col, "abs_quantity", "total_amount",
            "price_ratio", "qty_ratio", "log_amount",
            "is_cancellation", "is_off_hours", "is_weekend"
        ]

        feature_matrix = work_df[feature_cols].copy().fillna(0.0)

        # Rename standard display columns for response mapping
        work_df["_invoice_no"] = work_df[inv_col]
        work_df["_stock_code"] = work_df[sku_col]
        work_df["_description"] = work_df[desc_col]
        work_df["_customer_id"] = work_df[cust_col]
        work_df["_country"] = work_df[country_col]
        work_df["_invoice_date"] = dt_series.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("2023-01-01 00:00:00")
        work_df["_quantity"] = work_df[qty_col]
        work_df["_unit_price"] = work_df[price_col]

        return work_df, feature_matrix, feature_cols

    def train_and_detect(
        self,
        dataset_id: str,
        dataset_name: str,
        df: pd.DataFrame,
        mapping: dict[str, str],
        contamination: float = 0.03
    ) -> AnomalyResponse:
        """
        Train Isolation Forest model on transaction features, generate normalized
        anomaly scores, assign explainable pattern tags, and return audit records.
        """
        if len(df) < 20:
            return AnomalyResponse(
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                status="insufficient_data",
                message=f"Insufficient transactions: {len(df)} records provided (minimum 20 required for Isolation Forest).",
                total_records_analyzed=len(df),
                anomaly_count=0,
                contamination_rate=contamination,
                score_threshold=0.70,
                severity_breakdown={"critical": 0, "high": 0, "medium": 0, "low": 0},
                distribution_buckets=[],
                flagged_anomalies=[]
            )

        work_df, feat_matrix, feature_cols = self.extract_features(df, mapping)

        # Train Isolation Forest
        model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        model.fit(feat_matrix)

        # Save model artifact
        model_path = self._get_model_path(dataset_id)
        joblib.dump({"model": model, "feature_cols": feature_cols, "trained_at": datetime.now(timezone.utc).isoformat()}, model_path)

        # Compute raw scores and normalized scores in [0, 1]
        raw_scores = model.decision_function(feat_matrix)  # lower = more abnormal
        preds = model.predict(feat_matrix)  # -1 = anomaly, 1 = normal

        min_s, max_s = raw_scores.min(), raw_scores.max()
        score_range = max_s - min_s if max_s > min_s else 1.0
        # Invert so higher score = higher abnormality
        normalized_scores = (max_s - raw_scores) / score_range

        work_df["anomaly_score"] = np.round(normalized_scores, 4)
        work_df["is_anomaly"] = preds == -1

        # Determine threshold score for contamination cutoff
        anomaly_cutoff = float(np.percentile(normalized_scores, (1.0 - contamination) * 100))

        # Assign explainable suspicious pattern tags and severity
        flagged_records: list[AnomalyRecord] = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # Global 99th percentile thresholds for explainability
        p99_price = work_df["_unit_price"].quantile(0.99)
        p99_qty = work_df["abs_quantity"].quantile(0.99)
        p99_amount = work_df["total_amount"].abs().quantile(0.99)

        # Sort all anomalies by score descending
        anomalies_df = work_df[work_df["is_anomaly"]].sort_values("anomaly_score", ascending=False)

        for _, row in anomalies_df.iterrows():
            reasons = []
            score = float(row["anomaly_score"])

            # Rule 1: Extreme Unit Price
            if row["_unit_price"] > 3 * row["sku_median_price"] or row["_unit_price"] >= p99_price:
                reasons.append("EXTREME_UNIT_PRICE")

            # Rule 2: Unusual Bulk Quantity
            if row["abs_quantity"] > 4 * row["sku_median_qty"] or row["abs_quantity"] >= p99_qty:
                reasons.append("UNUSUAL_BULK_QUANTITY")

            # Rule 3: Cancellation Spike
            if row["is_cancellation"] == 1 and abs(row["total_amount"]) > 500.0:
                reasons.append("CANCELLATION_SPIKE")

            # Rule 4: Off-Hours Activity
            if row["is_off_hours"] == 1:
                reasons.append("OFF_HOURS_ACTIVITY")

            # Rule 5: High Value Transaction
            if abs(row["total_amount"]) >= p99_amount:
                reasons.append("HIGH_TRANSACTION_VALUE")

            # Fallback if no individual rule triggered
            if not reasons:
                reasons.append("MULTIDIMENSIONAL_OUTLIER")

            # Severity tiering
            if score >= 0.85 or len(reasons) >= 3:
                severity = "critical"
            elif score >= 0.70:
                severity = "high"
            elif score >= 0.55:
                severity = "medium"
            else:
                severity = "low"

            severity_counts[severity] += 1

            flagged_records.append(AnomalyRecord(
                invoice_no=str(row["_invoice_no"]),
                stock_code=str(row["_stock_code"]),
                description=str(row["_description"])[:60],
                quantity=round(float(row["_quantity"]), 2),
                unit_price=round(float(row["_unit_price"]), 2),
                total_amount=round(float(row["total_amount"]), 2),
                invoice_date=str(row["_invoice_date"]),
                customer_id=str(row["_customer_id"]),
                country=str(row["_country"]),
                anomaly_score=round(score, 4),
                risk_severity=severity,
                suspicious_reasons=reasons
            ))

        # Build score distribution histogram buckets (e.g. 5 bins from 0 to 1)
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.01]
        labels = ["0.0 – 0.2", "0.2 – 0.4", "0.4 – 0.6", "0.6 – 0.8", "0.8 – 1.0"]
        counts, _ = np.histogram(normalized_scores, bins=bins)

        distribution_buckets = [
            AnomalyDistributionBucket(
                score_range=label,
                count=int(c),
                is_anomaly_zone=(bins[i] >= 0.6)
            )
            for i, (label, c) in enumerate(zip(labels, counts))
        ]

        return AnomalyResponse(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            status="success",
            message=f"Isolation Forest identified {len(flagged_records)} anomalous transactions ({contamination*100:.1f}% contamination).",
            total_records_analyzed=len(df),
            anomaly_count=len(flagged_records),
            contamination_rate=contamination,
            score_threshold=round(anomaly_cutoff, 4),
            severity_breakdown=severity_counts,
            distribution_buckets=distribution_buckets,
            flagged_anomalies=flagged_records[:100],  # Return top 100 for responsive UI
            model_metadata={
                "model_name": "Isolation Forest (Unsupervised Tree Ensemble)",
                "n_estimators": 100,
                "contamination": contamination,
                "features_analyzed": feature_cols,
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "artifact_saved": str(model_path.name)
            }
        )

    def detect(
        self,
        dataset_id: str,
        df: Optional[pd.DataFrame] = None,
        mapping: Optional[dict[str, str]] = None,
        dataset_name: str = "Active Dataset",
        contamination: float = 0.03
    ) -> AnomalyResponse:
        """API wrapper for detecting anomalies."""
        if df is None or mapping is None:
            return AnomalyResponse(
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                status="error",
                message="DataFrame and column mapping required for anomaly detection.",
                total_records_analyzed=0,
                anomaly_count=0,
                contamination_rate=contamination,
                score_threshold=0.70,
                severity_breakdown={"critical": 0, "high": 0, "medium": 0, "low": 0},
                distribution_buckets=[],
                flagged_anomalies=[]
            )

        return self.train_and_detect(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            df=df,
            mapping=mapping,
            contamination=contamination
        )


# Global singleton instance
anomaly_service = AnomalyService()
