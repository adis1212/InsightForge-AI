"""Dataset processing service: file validation, parsing, quality analysis."""
import os
import uuid
from pathlib import Path
from typing import Optional, Any

import pandas as pd
import numpy as np

from app.core.config import settings
from app.core.exceptions import FileUploadError, ValidationError


# Standard column role patterns for auto-detection
COLUMN_PATTERNS = {
    "invoice_no": ["invoice", "invoiceno", "invoice_no", "invoicenumber", "order_id", "orderid", "order"],
    "stock_code": ["stockcode", "stock_code", "productcode", "product_code", "sku", "item_code", "itemcode"],
    "description": ["description", "productname", "product_name", "itemname", "item_name", "product", "item"],
    "quantity": ["quantity", "qty", "units", "amount", "count"],
    "unit_price": ["unitprice", "unit_price", "price", "rate", "mrp", "selling_price"],
    "unit_cost": ["unitcost", "unit_cost", "cogs", "cost", "purchase_price", "cost_price"],
    "customer_id": ["customerid", "customer_id", "custid", "cust_id", "client_id", "clientid", "buyer_id"],
    "country": ["country", "state", "city", "region", "location", "territory", "market", "mandi"],
    "date": ["invoicedate", "invoice_date", "date", "orderdate", "order_date", "transaction_date", "transactiondate"],
}


def validate_file(filename: str, file_size: int) -> None:
    """Validate uploaded file type and size."""
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise FileUploadError(
            f"File type '{ext}' not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise FileUploadError(
            f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds limit ({settings.MAX_UPLOAD_SIZE_MB} MB)"
        )


def save_upload(file_content: bytes, filename: str, workspace_id: str) -> str:
    """Save uploaded file to disk and return the path."""
    upload_dir = Path(settings.UPLOAD_DIR) / workspace_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}_{Path(filename).name}"
    file_path = upload_dir / safe_name
    file_path.write_bytes(file_content)
    return str(file_path)


def read_dataset(file_path: str) -> pd.DataFrame:
    """Read a CSV or XLSX file into a DataFrame."""
    ext = Path(file_path).suffix.lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            raise ValidationError(f"Unsupported file type: {ext}")
    except Exception as e:
        if isinstance(e, (FileUploadError, ValidationError)):
            raise
        raise ValidationError(f"Failed to read file: {str(e)}")

    if df.empty:
        raise ValidationError("File contains no data")

    return df


def auto_detect_columns(df: pd.DataFrame) -> dict[str, str]:
    """Automatically detect column roles using pattern matching."""
    mapping: dict[str, str] = {}
    normalized = {col: col.lower().replace(" ", "").replace("_", "") for col in df.columns}

    for role, patterns in COLUMN_PATTERNS.items():
        for col, norm_col in normalized.items():
            if norm_col in [p.replace("_", "") for p in patterns]:
                mapping[role] = col
                break

    return mapping


def analyze_quality(df: pd.DataFrame, column_mapping: dict[str, str]) -> dict[str, Any]:
    """Generate a data quality report for the dataset."""
    total_rows = len(df)
    total_columns = len(df.columns)

    # Missing values per column
    missing_values = df.isnull().sum().to_dict()
    missing_values = {k: int(v) for k, v in missing_values.items() if v > 0}

    missing_percentages = {
        k: round(v / total_rows * 100, 2) if total_rows > 0 else 0.0
        for k, v in missing_values.items()
    }

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    duplicate_percentage = round(duplicate_rows / total_rows * 100, 2) if total_rows > 0 else 0.0

    # Date validation
    date_issues = 0
    date_col = column_mapping.get("date")
    if date_col and date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        date_issues = int(dates.isnull().sum()) - int(df[date_col].isnull().sum())
        date_issues = max(0, date_issues)  # Only count parse failures, not original nulls

    # Quantity issues
    negative_quantities = 0
    qty_col = column_mapping.get("quantity")
    if qty_col and qty_col in df.columns:
        qty = pd.to_numeric(df[qty_col], errors="coerce")
        negative_quantities = int((qty < 0).sum())

    # Price issues
    zero_prices = 0
    price_col = column_mapping.get("unit_price")
    if price_col and price_col in df.columns:
        prices = pd.to_numeric(df[price_col], errors="coerce")
        zero_prices = int((prices <= 0).sum())

    # Cancellation count
    cancellation_count = 0
    invoice_col = column_mapping.get("invoice_no")
    if invoice_col and invoice_col in df.columns:
        invoices = df[invoice_col].astype(str)
        cancellation_count = int(invoices.str.startswith("C", na=False).sum())

    # Compute quality score (0-100)
    deductions = 0
    if total_rows > 0:
        total_missing_pct = df.isnull().sum().sum() / (total_rows * total_columns) * 100 if total_columns > 0 else 0
        deductions += min(total_missing_pct * 2, 30)  # Up to 30 points for missing data
        deductions += min(duplicate_percentage, 20)  # Up to 20 points for duplicates
        if date_issues > 0:
            deductions += min(date_issues / total_rows * 100 * 2, 15)
        if negative_quantities > 0:
            deductions += min(negative_quantities / total_rows * 100 * 2, 15)
        if zero_prices > 0:
            deductions += min(zero_prices / total_rows * 100 * 2, 10)

    quality_score = round(max(0, 100 - deductions), 1)

    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "missing_values": missing_values,
        "missing_percentages": missing_percentages,
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": duplicate_percentage,
        "date_issues": date_issues,
        "negative_quantities": negative_quantities,
        "zero_prices": zero_prices,
        "cancellation_count": cancellation_count,
        "data_quality_score": quality_score,
    }


def get_column_metadata(df: pd.DataFrame, column_mapping: dict[str, str]) -> list[dict[str, Any]]:
    """Extract metadata for each column."""
    columns_meta = []
    reverse_mapping = {v: k for k, v in column_mapping.items()}

    for col in df.columns:
        sample = df[col].dropna().head(5).tolist()
        # Convert numpy types to Python types for JSON serialization
        sample = [
            x.item() if hasattr(x, "item") else str(x) if not isinstance(x, (int, float, str, bool)) else x
            for x in sample
        ]
        columns_meta.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "mapped_role": reverse_mapping.get(col),
            "null_count": int(df[col].isnull().sum()),
            "unique_count": int(df[col].nunique()),
            "sample_values": sample,
        })

    return columns_meta
