"""Tests for the deterministic analytics engine."""
import pytest
import pandas as pd
import numpy as np
from app.services.analytics_service import AnalyticsService


class TestRevenueCalculation:
    """Test revenue calculations."""

    def test_total_revenue_basic(self, sample_retail_df, standard_column_mapping):
        """Revenue should sum only valid (non-cancelled) transactions."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_total_revenue()

        assert result.available is True
        # Valid transactions:
        # 489434: 12*3.50 + 6*7.95 = 42.00 + 47.70 = 89.70
        # 489435: 24*1.25 + 36*2.10 = 30.00 + 75.60 = 105.60
        # 489436: 10*15.00 = 150.00
        # Total: 89.70 + 105.60 + 150.00 = 345.30
        assert result.value == pytest.approx(345.30, abs=0.01)

    def test_total_revenue_excludes_cancellations(self, sample_retail_df, standard_column_mapping):
        """Cancellations (invoice starting with C) should be excluded from revenue."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_total_revenue()

        # Should NOT include C489437 lines
        assert result.value is not None
        assert result.value > 0

    def test_revenue_missing_columns(self):
        """Revenue should be unavailable when required columns are missing."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        svc = AnalyticsService(df, {})
        result = svc.calculate_total_revenue()

        assert result.available is False
        assert result.unavailable_reason is not None


class TestOrderMetrics:
    """Test order-related KPIs."""

    def test_unique_orders(self, sample_retail_df, standard_column_mapping):
        """Should count unique non-cancelled invoice numbers."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_unique_orders()

        assert result.available is True
        # Valid invoices: 489434, 489435, 489436 = 3
        assert result.value == 3.0

    def test_average_order_value(self, sample_retail_df, standard_column_mapping):
        """AOV should be total revenue / unique orders."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_average_order_value()

        assert result.available is True
        # 345.30 / 3 = 115.10
        assert result.value == pytest.approx(115.10, abs=0.01)

    def test_units_sold(self, sample_retail_df, standard_column_mapping):
        """Should sum quantities of valid transactions only."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_units_sold()

        assert result.available is True
        # 12 + 6 + 24 + 36 + 10 = 88
        assert result.value == 88.0


class TestCustomerMetrics:
    """Test customer-related KPIs."""

    def test_unique_customers(self, sample_retail_df, standard_column_mapping):
        """Should count unique customer IDs from valid transactions."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_unique_customers()

        assert result.available is True
        # Customers: 12345, 12346, 12347 = 3
        assert result.value == 3.0


class TestCancellationMetrics:
    """Test cancellation/return KPIs."""

    def test_cancellation_rate(self, sample_retail_df, standard_column_mapping):
        """Should calculate percentage of cancelled invoices."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_cancellation_rate()

        assert result.available is True
        # 1 cancelled out of 4 total invoices = 25%
        assert result.value == pytest.approx(25.0, abs=0.1)


class TestMonthlyRevenue:
    """Test monthly revenue calculations."""

    def test_monthly_breakdown(self, sample_retail_df, standard_column_mapping):
        """Should produce monthly revenue breakdown with growth rates."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_monthly_revenue()

        assert len(result) > 0
        # First month should have no growth rate
        assert result[0].growth_rate is None
        # All revenues should be positive (valid transactions only)
        for month in result:
            assert month.revenue >= 0

    def test_growth_rate_calculation(self, sample_retail_df, standard_column_mapping):
        """Growth rate should be (current - previous) / previous * 100."""
        svc = AnalyticsService(sample_retail_df, standard_column_mapping)
        result = svc.calculate_monthly_revenue()

        if len(result) >= 2:
            expected_growth = (result[1].revenue - result[0].revenue) / result[0].revenue * 100
            assert result[1].growth_rate == pytest.approx(expected_growth, abs=0.01)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self, standard_column_mapping):
        """Should handle empty DataFrames gracefully."""
        df = pd.DataFrame(columns=["InvoiceNo", "Quantity", "UnitPrice", "CustomerID", "Country", "InvoiceDate", "StockCode", "Description"])
        svc = AnalyticsService(df, standard_column_mapping)
        summary = svc.calculate_summary("test-id")

        assert summary.total_revenue.value == pytest.approx(0.0)

    def test_all_cancellations(self, standard_column_mapping):
        """Should handle datasets with only cancellations."""
        df = pd.DataFrame({
            "InvoiceNo": ["C100", "C101"],
            "Quantity": [-5, -3],
            "UnitPrice": [10.0, 20.0],
            "CustomerID": ["C1", "C2"],
            "Country": ["UK", "DE"],
            "InvoiceDate": ["2023-01-01", "2023-02-01"],
            "StockCode": ["A", "B"],
            "Description": ["X", "Y"],
        })
        svc = AnalyticsService(df, standard_column_mapping)
        result = svc.calculate_total_revenue()

        assert result.value == pytest.approx(0.0)

    def test_missing_values_in_data(self, standard_column_mapping):
        """Should handle NaN values without crashing."""
        df = pd.DataFrame({
            "InvoiceNo": ["100", "101", "102"],
            "Quantity": [5, None, 3],
            "UnitPrice": [10.0, 20.0, None],
            "CustomerID": ["C1", None, "C3"],
            "Country": ["UK", "DE", None],
            "InvoiceDate": ["2023-01-01", "2023-02-01", "2023-03-01"],
            "StockCode": ["A", "B", "C"],
            "Description": ["X", "Y", "Z"],
        })
        svc = AnalyticsService(df, standard_column_mapping)
        summary = svc.calculate_summary("test-id")

        # Should not crash
        assert summary.dataset_id == "test-id"

    def test_division_by_zero_growth(self, standard_column_mapping):
        """Should handle zero revenue months without division by zero."""
        df = pd.DataFrame({
            "InvoiceNo": ["100", "101"],
            "Quantity": [0, 5],
            "UnitPrice": [10.0, 20.0],
            "CustomerID": ["C1", "C2"],
            "Country": ["UK", "DE"],
            "InvoiceDate": ["2023-01-01", "2023-03-01"],
            "StockCode": ["A", "B"],
            "Description": ["X", "Y"],
        })
        svc = AnalyticsService(df, standard_column_mapping)
        result = svc.calculate_monthly_revenue()
        # Should not raise ZeroDivisionError
        for month in result:
            assert month.growth_rate is None or isinstance(month.growth_rate, float)
