"""Tests for dataset service: validation, parsing, quality analysis."""
import pytest
import os
import tempfile
import pandas as pd
from app.services.dataset_service import (
    validate_file, auto_detect_columns, analyze_quality,
    read_dataset, get_column_metadata,
)
from app.core.exceptions import FileUploadError, ValidationError


class TestFileValidation:
    """Test file upload validation."""

    def test_valid_csv(self):
        """CSV files should pass validation."""
        validate_file("data.csv", 1024)  # Should not raise

    def test_valid_xlsx(self):
        """XLSX files should pass validation."""
        validate_file("report.xlsx", 1024)  # Should not raise

    def test_invalid_extension(self):
        """Non-CSV/XLSX files should be rejected."""
        with pytest.raises(FileUploadError):
            validate_file("script.py", 1024)

    def test_file_too_large(self):
        """Files exceeding size limit should be rejected."""
        with pytest.raises(FileUploadError):
            validate_file("huge.csv", 100 * 1024 * 1024)  # 100 MB

    def test_empty_filename(self):
        """Files with unknown extension should be rejected."""
        with pytest.raises(FileUploadError):
            validate_file("noext", 1024)


class TestColumnAutoDetection:
    """Test automatic column role detection."""

    def test_standard_retail_columns(self):
        """Should detect standard UCI Online Retail II column names."""
        df = pd.DataFrame(columns=[
            "Invoice", "StockCode", "Description", "Quantity",
            "InvoiceDate", "Price", "Customer ID", "Country",
        ])
        mapping = auto_detect_columns(df)

        assert mapping.get("invoice_no") == "Invoice"
        assert mapping.get("stock_code") == "StockCode"
        assert mapping.get("quantity") == "Quantity"
        assert mapping.get("country") == "Country"

    def test_custom_column_names(self):
        """Should detect common alternative column names."""
        df = pd.DataFrame(columns=["OrderID", "SKU", "Qty", "UnitPrice", "Region"])
        mapping = auto_detect_columns(df)
        # 'Qty' normalizes to 'qty' which matches 'quantity' patterns
        assert "quantity" in mapping

    def test_no_matching_columns(self):
        """Should return empty mapping when no columns match."""
        df = pd.DataFrame(columns=["xyz", "abc", "foo"])
        mapping = auto_detect_columns(df)
        assert len(mapping) == 0


class TestQualityAnalysis:
    """Test data quality report generation."""

    def test_quality_with_clean_data(self):
        """Clean data should get a high quality score."""
        df = pd.DataFrame({
            "InvoiceNo": ["100", "101", "102"],
            "Quantity": [5, 10, 3],
            "UnitPrice": [10.0, 20.0, 5.0],
            "CustomerID": ["C1", "C2", "C3"],
            "Country": ["UK", "DE", "FR"],
            "InvoiceDate": ["2023-01-01", "2023-02-01", "2023-03-01"],
        })
        mapping = {"invoice_no": "InvoiceNo", "quantity": "Quantity",
                    "unit_price": "UnitPrice", "customer_id": "CustomerID",
                    "country": "Country", "date": "InvoiceDate"}
        report = analyze_quality(df, mapping)

        assert report["total_rows"] == 3
        assert report["duplicate_rows"] == 0
        assert report["data_quality_score"] >= 90

    def test_quality_detects_missing_values(self):
        """Should count missing values per column."""
        df = pd.DataFrame({
            "A": [1, None, 3],
            "B": [None, None, "x"],
        })
        report = analyze_quality(df, {})

        assert report["missing_values"]["A"] == 1
        assert report["missing_values"]["B"] == 2

    def test_quality_detects_duplicates(self):
        """Should count duplicate rows."""
        df = pd.DataFrame({
            "A": [1, 1, 2],
            "B": ["x", "x", "y"],
        })
        report = analyze_quality(df, {})
        assert report["duplicate_rows"] == 1

    def test_quality_detects_cancellations(self):
        """Should count invoices starting with C."""
        df = pd.DataFrame({
            "InvoiceNo": ["100", "C101", "C102", "103"],
        })
        mapping = {"invoice_no": "InvoiceNo"}
        report = analyze_quality(df, mapping)
        assert report["cancellation_count"] == 2

    def test_quality_detects_negative_quantities(self):
        """Should count negative quantities."""
        df = pd.DataFrame({
            "Quantity": [5, -3, 10, -1],
        })
        mapping = {"quantity": "Quantity"}
        report = analyze_quality(df, mapping)
        assert report["negative_quantities"] == 2


class TestReadDataset:
    """Test file reading."""

    def test_read_csv(self):
        """Should read a CSV file into DataFrame."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("A,B,C\n1,2,3\n4,5,6\n")
            f.flush()
            df = read_dataset(f.name)
            assert len(df) == 2
            assert list(df.columns) == ["A", "B", "C"]
        os.unlink(f.name)

    def test_read_empty_csv(self):
        """Should raise error for empty files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            f.flush()
            with pytest.raises(ValidationError):
                read_dataset(f.name)
        os.unlink(f.name)
