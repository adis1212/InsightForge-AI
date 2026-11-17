"""Tests for Isolation Forest Anomaly Detection Service (Stage 6).

Covers:
1. Transaction-level feature extraction (SKU deviations, off-hours, cancellations).
2. Isolation Forest model training and normalized continuous anomaly scoring.
3. Explainable pattern tags and risk severity assignment.
4. Synthetic anomaly injection test (precision/recall validation).
5. Source record reference preservation.
6. Score distribution histogram generation.
7. Insufficient data handling.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from app.services.anomaly_service import AnomalyService

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
def anomaly_service_tmp(tmp_path):
    """Anomaly service instance using isolated temporary directory."""
    return AnomalyService(models_dir=tmp_path)


class TestFeatureExtraction:
    """Verify transaction-level feature engineering."""

    def test_feature_matrix_shapes_and_columns(self, anomaly_service_tmp, wholesale_df):
        work_df, feat_matrix, feat_cols = anomaly_service_tmp.extract_features(wholesale_df, MAPPING)
        assert len(feat_matrix) == len(wholesale_df)
        assert len(work_df) == len(wholesale_df)
        assert "price_ratio" in feat_matrix.columns
        assert "qty_ratio" in feat_matrix.columns
        assert "is_cancellation" in feat_matrix.columns
        assert "is_off_hours" in feat_matrix.columns
        assert "is_weekend" in feat_matrix.columns
        assert not feat_matrix.isna().any().any()

    def test_cancellation_and_off_hours_flags(self, anomaly_service_tmp):
        test_df = pd.DataFrame([
            {"InvoiceNo": "1001", "StockCode": "WH001", "Description": "Item 1", "Quantity": 10, "UnitPrice": 20.0, "CustomerID": "C1", "Country": "UK", "InvoiceDate": "2023-01-05 14:00:00"},
            {"InvoiceNo": "C1002", "StockCode": "WH001", "Description": "Item 1", "Quantity": -2, "UnitPrice": 20.0, "CustomerID": "C1", "Country": "UK", "InvoiceDate": "2023-01-06 02:30:00"},
        ])
        work_df, feat_matrix, _ = anomaly_service_tmp.extract_features(test_df, MAPPING)
        # First row: normal hours (14:00), not cancellation
        assert feat_matrix.loc[0, "is_cancellation"] == 0
        assert feat_matrix.loc[0, "is_off_hours"] == 0
        # Second row: cancellation (C-prefix), off-hours (02:30)
        assert feat_matrix.loc[1, "is_cancellation"] == 1
        assert feat_matrix.loc[1, "is_off_hours"] == 1


class TestIsolationForestTrainingAndScoring:
    """Verify unsupervised outlier detection and scoring."""

    def test_detect_anomalies_success(self, anomaly_service_tmp, wholesale_df):
        resp = anomaly_service_tmp.train_and_detect(
            dataset_id="test_wholesale_anomalies",
            dataset_name="Synthetic Wholesale",
            df=wholesale_df,
            mapping=MAPPING,
            contamination=0.03
        )

        assert resp.status == "success"
        assert resp.total_records_analyzed == len(wholesale_df)
        assert resp.anomaly_count > 0
        assert resp.contamination_rate == 0.03

        # Scores must be bounded in [0, 1]
        for anom in resp.flagged_anomalies:
            assert 0.0 <= anom.anomaly_score <= 1.0
            assert anom.risk_severity in ["critical", "high", "medium", "low"]
            assert len(anom.suspicious_reasons) > 0

        # Score distribution histogram
        assert len(resp.distribution_buckets) == 5
        total_bucket_count = sum(b.count for b in resp.distribution_buckets)
        assert total_bucket_count == len(wholesale_df)

    def test_source_record_references_preserved(self, anomaly_service_tmp, wholesale_df):
        resp = anomaly_service_tmp.train_and_detect(
            dataset_id="test_refs",
            dataset_name="Synthetic Wholesale",
            df=wholesale_df,
            mapping=MAPPING,
            contamination=0.02
        )

        top_anomaly = resp.flagged_anomalies[0]
        assert top_anomaly.invoice_no is not None
        assert top_anomaly.stock_code is not None
        assert top_anomaly.description is not None
        assert top_anomaly.customer_id is not None
        assert top_anomaly.country is not None
        assert top_anomaly.total_amount == pytest.approx(top_anomaly.quantity * top_anomaly.unit_price, rel=1e-2)


class TestSyntheticAnomalyInjection:
    """Empirical evaluation: Inject known synthetic anomalies and test recall."""

    def test_detects_injected_synthetic_anomalies(self, anomaly_service_tmp, wholesale_df):
        clean_subset = wholesale_df.iloc[:500].copy()

        # Inject 4 distinct anomaly patterns:
        injected_rows = pd.DataFrame([
            # 1. Extreme 100x unit price spike
            {"InvoiceNo": "INJ-901", "StockCode": "WH0015", "Description": "Diesel Generator 5kW", "Quantity": 2, "UnitPrice": 45000.0, "CustomerID": "C99901", "Country": "UK", "InvoiceDate": "2023-06-15 11:00:00"},
            # 2. Extreme bulk quantity order (500x median)
            {"InvoiceNo": "INJ-902", "StockCode": "WH0000", "Description": "Industrial Lubricant 5L", "Quantity": 5000, "UnitPrice": 42.50, "CustomerID": "C99902", "Country": "Germany", "InvoiceDate": "2023-06-16 14:00:00"},
            # 3. Severe cancellation reversal
            {"InvoiceNo": "CINJ-903", "StockCode": "WH0018", "Description": "Transformer Oil 20L", "Quantity": -800, "UnitPrice": 195.0, "CustomerID": "C99903", "Country": "France", "InvoiceDate": "2023-06-17 16:00:00"},
            # 4. Off-hours extreme transaction
            {"InvoiceNo": "INJ-904", "StockCode": "WH0011", "Description": "Bearing 6205-2RS", "Quantity": 3500, "UnitPrice": 14.20, "CustomerID": "C99904", "Country": "Spain", "InvoiceDate": "2023-06-18 03:15:00"},
        ])

        test_data = pd.concat([clean_subset, injected_rows], ignore_index=True)

        resp = anomaly_service_tmp.train_and_detect(
            dataset_id="injection_test",
            dataset_name="Injected Benchmark",
            df=test_data,
            mapping=MAPPING,
            contamination=0.04
        )

        flagged_invoices = {a.invoice_no for a in resp.flagged_anomalies}

        # Check detection recall on the 4 injected anomalies
        detected_count = sum(1 for inv in ["INJ-901", "INJ-902", "CINJ-903", "INJ-904"] if inv in flagged_invoices)
        recall = detected_count / 4.0

        # At least 3 out of 4 (75% to 100%) must be detected
        assert recall >= 0.75, f"Expected recall >= 75%, got {recall*100}% (detected {detected_count}/4)"

        # Verify the extreme unit price anomaly has the EXTREME_UNIT_PRICE reason
        price_anomaly = next((a for a in resp.flagged_anomalies if a.invoice_no == "INJ-901"), None)
        assert price_anomaly is not None
        assert "EXTREME_UNIT_PRICE" in price_anomaly.suspicious_reasons


class TestAnomalyEdgeCases:
    """Verify data sufficiency and edge case handling."""

    def test_insufficient_records_refusal(self, anomaly_service_tmp):
        tiny_df = pd.DataFrame([
            {"InvoiceNo": "1", "StockCode": "A", "Description": "Item", "Quantity": 1, "UnitPrice": 10.0, "CustomerID": "C1", "Country": "UK", "InvoiceDate": "2023-01-01"},
            {"InvoiceNo": "2", "StockCode": "A", "Description": "Item", "Quantity": 2, "UnitPrice": 10.0, "CustomerID": "C1", "Country": "UK", "InvoiceDate": "2023-01-02"},
        ])
        resp = anomaly_service_tmp.train_and_detect(
            dataset_id="tiny_test",
            dataset_name="Tiny Data",
            df=tiny_df,
            mapping=MAPPING
        )
        assert resp.status == "insufficient_data"
        assert "Insufficient transactions" in resp.message
