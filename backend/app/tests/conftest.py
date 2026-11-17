"""Pytest configuration and fixtures."""
import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_retail_df():
    """Create a sample retail-style DataFrame for testing."""
    import pandas as pd
    data = {
        "InvoiceNo": ["489434", "489434", "489435", "489435", "489436", "C489437", "C489437"],
        "StockCode": ["85048", "79323P", "22350", "22349", "84879", "85048", "22350"],
        "Description": ["Widget A", "Widget B", "Widget C", "Widget D", "Widget E", "Widget A", "Widget C"],
        "Quantity": [12, 6, 24, 36, 10, -12, -24],
        "InvoiceDate": [
            "2023-01-15 10:00:00", "2023-01-15 10:00:00",
            "2023-02-20 11:00:00", "2023-02-20 11:00:00",
            "2023-03-10 09:00:00",
            "2023-01-20 14:00:00", "2023-01-20 14:00:00",
        ],
        "UnitPrice": [3.50, 7.95, 1.25, 2.10, 15.00, 3.50, 1.25],
        "CustomerID": ["12345", "12345", "12346", "12346", "12347", "12345", "12346"],
        "Country": ["United Kingdom", "United Kingdom", "Germany", "Germany", "France", "United Kingdom", "Germany"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def standard_column_mapping():
    """Standard column mapping for the sample dataset."""
    return {
        "invoice_no": "InvoiceNo",
        "stock_code": "StockCode",
        "description": "Description",
        "quantity": "Quantity",
        "date": "InvoiceDate",
        "unit_price": "UnitPrice",
        "customer_id": "CustomerID",
        "country": "Country",
    }
