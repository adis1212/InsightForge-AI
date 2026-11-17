"""Deterministic KPI analytics engine using Pandas.

This module performs ALL numerical calculations deterministically.
LLMs must NEVER be used for numerical computation.
"""
import pandas as pd
import numpy as np
from typing import Optional, Any
from app.schemas.analytics import (
    KPIValue, KPISummary, RevenueGrowth, ProductRanking,
    GeographicPerformance, AnalyticsResponse,
)


class AnalyticsService:
    """Deterministic analytics engine using Pandas."""

    # Standard column role mappings
    ROLE_INVOICE = "invoice_no"
    ROLE_STOCK_CODE = "stock_code"
    ROLE_DESCRIPTION = "description"
    ROLE_QUANTITY = "quantity"
    ROLE_PRICE = "unit_price"
    ROLE_CUSTOMER_ID = "customer_id"
    ROLE_COUNTRY = "country"
    ROLE_DATE = "date"
    ROLE_UNIT_COST = "unit_cost"
    ROLE_CATEGORY = "category"
    ROLE_CITY = "city"

    def __init__(self, df: pd.DataFrame, column_mapping: dict[str, str], currency: str = "USD"):
        """
        Initialize with a DataFrame, column mapping, and currency code.

        Args:
            df: Raw DataFrame from the uploaded file.
            column_mapping: Maps standard role names to actual column names.
            currency: Currency code (USD, INR, etc.) for formatted output.
        """
        self.raw_df = df.copy()
        self.mapping = column_mapping
        self.currency = currency.upper()
        self.df = self._prepare_data()

    def _fmt_currency(self, value: float) -> str:
        """Format currency value according to configured currency."""
        if self.currency == "INR":
            # Indian number grouping: lakhs and crores
            if abs(value) >= 1e7:
                return f"₹{value / 1e7:,.2f} Cr"
            if abs(value) >= 1e5:
                return f"₹{value / 1e5:,.2f} Lakh"
            return f"₹{value:,.2f}"
        return f"${value:,.2f}"

    def _get_col(self, role: str) -> Optional[str]:
        """Get actual column name for a standard role."""
        return self.mapping.get(role)

    def _prepare_data(self) -> pd.DataFrame:
        """Prepare data for analysis: type conversions and cleaning."""
        df = self.raw_df.copy()

        # Parse date column
        date_col = self._get_col(self.ROLE_DATE)
        if date_col and date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        # Parse numeric columns
        qty_col = self._get_col(self.ROLE_QUANTITY)
        if qty_col and qty_col in df.columns:
            df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce")

        price_col = self._get_col(self.ROLE_PRICE)
        if price_col and price_col in df.columns:
            df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

        # Compute line total (revenue per line)
        if qty_col and price_col and qty_col in df.columns and price_col in df.columns:
            df["_line_total"] = df[qty_col] * df[price_col]

        return df

    def _get_valid_transactions(self) -> pd.DataFrame:
        """Filter to valid (non-cancelled) transactions with positive quantity."""
        df = self.df.copy()
        qty_col = self._get_col(self.ROLE_QUANTITY)
        invoice_col = self._get_col(self.ROLE_INVOICE)

        if qty_col and qty_col in df.columns:
            df = df[df[qty_col] > 0]

        # Exclude cancellations (invoices starting with 'C')
        if invoice_col and invoice_col in df.columns:
            df[invoice_col] = df[invoice_col].astype(str)
            df = df[~df[invoice_col].str.startswith("C", na=False)]

        return df

    def _get_cancellations(self) -> pd.DataFrame:
        """Filter to cancellation records only."""
        df = self.df.copy()
        invoice_col = self._get_col(self.ROLE_INVOICE)

        if invoice_col and invoice_col in df.columns:
            df[invoice_col] = df[invoice_col].astype(str)
            return df[df[invoice_col].str.startswith("C", na=False)]

        return pd.DataFrame()

    def calculate_total_revenue(self) -> KPIValue:
        """Calculate total revenue from valid transactions."""
        try:
            valid = self._get_valid_transactions()
            if "_line_total" not in valid.columns:
                return KPIValue(
                    name="Total Revenue",
                    available=False,
                    unavailable_reason="Quantity and/or price columns not mapped",
                    description="Sum of (quantity × unit price) for valid transactions",
                )
            revenue = float(valid["_line_total"].sum())
            return KPIValue(
                name="Total Revenue",
                value=revenue,
                formatted=self._fmt_currency(revenue),
                description="Sum of (quantity × unit price) for valid transactions",
            )
        except Exception as e:
            return KPIValue(
                name="Total Revenue",
                available=False,
                unavailable_reason=f"Calculation error: {str(e)}",
                description="Sum of (quantity × unit price) for valid transactions",
            )

    def calculate_unique_orders(self) -> KPIValue:
        """Calculate number of unique orders."""
        invoice_col = self._get_col(self.ROLE_INVOICE)
        if not invoice_col or invoice_col not in self.df.columns:
            return KPIValue(
                name="Unique Orders",
                available=False,
                unavailable_reason="Invoice column not mapped",
                description="Count of distinct invoice numbers",
            )
        valid = self._get_valid_transactions()
        count = int(valid[invoice_col].nunique())
        return KPIValue(
            name="Unique Orders",
            value=float(count),
            formatted=f"{count:,}",
            description="Count of distinct invoice numbers (excluding cancellations)",
        )

    def calculate_units_sold(self) -> KPIValue:
        """Calculate total units sold."""
        qty_col = self._get_col(self.ROLE_QUANTITY)
        if not qty_col or qty_col not in self.df.columns:
            return KPIValue(
                name="Units Sold",
                available=False,
                unavailable_reason="Quantity column not mapped",
                description="Total quantity of items sold",
            )
        valid = self._get_valid_transactions()
        total = int(valid[qty_col].sum())
        return KPIValue(
            name="Units Sold",
            value=float(total),
            formatted=f"{total:,}",
            description="Total quantity of items sold (excluding cancellations)",
        )

    def calculate_average_order_value(self) -> KPIValue:
        """Calculate average order value (AOV)."""
        invoice_col = self._get_col(self.ROLE_INVOICE)
        if not invoice_col or "_line_total" not in self._get_valid_transactions().columns:
            return KPIValue(
                name="Average Order Value",
                available=False,
                unavailable_reason="Invoice and/or revenue columns not available",
                description="Mean revenue per order",
            )
        valid = self._get_valid_transactions()
        order_totals = valid.groupby(invoice_col)["_line_total"].sum()

        if len(order_totals) == 0:
            return KPIValue(
                name="Average Order Value",
                value=0.0,
                formatted=self._fmt_currency(0.0),
                description="Mean revenue per order (no valid orders found)",
            )

        aov = float(order_totals.mean())
        return KPIValue(
            name="Average Order Value",
            value=aov,
            formatted=self._fmt_currency(aov),
            description="Mean revenue per order",
        )

    def calculate_unique_customers(self) -> KPIValue:
        """Calculate number of unique customers."""
        cust_col = self._get_col(self.ROLE_CUSTOMER_ID)
        if not cust_col or cust_col not in self.df.columns:
            return KPIValue(
                name="Unique Customers",
                available=False,
                unavailable_reason="Customer ID column not mapped",
                description="Count of distinct customer identifiers",
            )
        valid = self._get_valid_transactions()
        # Drop NaN customer IDs
        count = int(valid[cust_col].dropna().nunique())
        return KPIValue(
            name="Unique Customers",
            value=float(count),
            formatted=f"{count:,}",
            description="Count of distinct customer identifiers",
        )

    def calculate_cancellation_rate(self) -> KPIValue:
        """Calculate cancellation/return rate."""
        invoice_col = self._get_col(self.ROLE_INVOICE)
        if not invoice_col or invoice_col not in self.df.columns:
            return KPIValue(
                name="Cancellation Rate",
                available=False,
                unavailable_reason="Invoice column not mapped",
                description="Percentage of cancelled invoices",
            )
        all_invoices = self.df[invoice_col].astype(str).nunique()
        cancellations = self._get_cancellations()
        cancel_count = cancellations[invoice_col].astype(str).nunique() if len(cancellations) > 0 else 0

        if all_invoices == 0:
            rate = 0.0
        else:
            rate = float(cancel_count / all_invoices * 100)

        return KPIValue(
            name="Cancellation Rate",
            value=rate,
            formatted=f"{rate:.1f}%",
            description="Percentage of invoices that are cancellations",
        )

    def calculate_summary(self, dataset_id: str) -> KPISummary:
        """Calculate all summary KPIs."""
        return KPISummary(
            dataset_id=dataset_id,
            total_revenue=self.calculate_total_revenue(),
            unique_orders=self.calculate_unique_orders(),
            units_sold=self.calculate_units_sold(),
            average_order_value=self.calculate_average_order_value(),
            unique_customers=self.calculate_unique_customers(),
            cancellation_rate=self.calculate_cancellation_rate(),
        )

    def calculate_monthly_revenue(self) -> list[RevenueGrowth]:
        """Calculate monthly revenue with growth rates."""
        date_col = self._get_col(self.ROLE_DATE)
        if not date_col or date_col not in self.df.columns or "_line_total" not in self._get_valid_transactions().columns:
            return []

        valid = self._get_valid_transactions()
        valid = valid.dropna(subset=[date_col])

        if len(valid) == 0:
            return []

        monthly = valid.set_index(date_col).resample("ME")["_line_total"].sum().reset_index()
        monthly.columns = ["date", "revenue"]
        monthly = monthly.sort_values("date")

        results = []
        prev_revenue = None
        for _, row in monthly.iterrows():
            revenue = float(row["revenue"])
            growth_rate = None
            if prev_revenue is not None and prev_revenue != 0:
                growth_rate = float((revenue - prev_revenue) / prev_revenue * 100)
            elif prev_revenue == 0:
                growth_rate = None  # Avoid division by zero

            results.append(RevenueGrowth(
                period=row["date"].strftime("%Y-%m"),
                revenue=revenue,
                growth_rate=growth_rate,
            ))
            prev_revenue = revenue

        return results

    def calculate_top_products(self, limit: int = 10) -> list[ProductRanking]:
        """Calculate top products by revenue."""
        stock_col = self._get_col(self.ROLE_STOCK_CODE)
        desc_col = self._get_col(self.ROLE_DESCRIPTION)
        qty_col = self._get_col(self.ROLE_QUANTITY)

        if not stock_col or "_line_total" not in self._get_valid_transactions().columns:
            return []

        valid = self._get_valid_transactions()

        agg_dict: dict[str, Any] = {"_line_total": "sum"}
        if qty_col and qty_col in valid.columns:
            agg_dict[qty_col] = "sum"

        grouped = valid.groupby(stock_col).agg(agg_dict).reset_index()
        grouped = grouped.sort_values("_line_total", ascending=False).head(limit)

        # Get descriptions
        if desc_col and desc_col in valid.columns:
            desc_map = valid.groupby(stock_col)[desc_col].first().to_dict()
        else:
            desc_map = {}

        results = []
        for rank, (_, row) in enumerate(grouped.iterrows(), 1):
            results.append(ProductRanking(
                rank=rank,
                stock_code=str(row[stock_col]),
                description=str(desc_map.get(row[stock_col], "N/A")),
                total_revenue=float(row["_line_total"]),
                units_sold=int(row.get(qty_col, 0)) if qty_col else 0,
            ))

        return results

    def calculate_geographic_performance(self) -> list[GeographicPerformance]:
        """Calculate performance by country/region."""
        country_col = self._get_col(self.ROLE_COUNTRY)
        invoice_col = self._get_col(self.ROLE_INVOICE)
        cust_col = self._get_col(self.ROLE_CUSTOMER_ID)

        if not country_col or country_col not in self.df.columns:
            return []

        valid = self._get_valid_transactions()

        agg_dict: dict[str, Any] = {}
        if "_line_total" in valid.columns:
            agg_dict["_line_total"] = "sum"
        if invoice_col and invoice_col in valid.columns:
            agg_dict[invoice_col] = "nunique"
        if cust_col and cust_col in valid.columns:
            agg_dict[cust_col] = "nunique"

        if not agg_dict:
            return []

        grouped = valid.groupby(country_col).agg(agg_dict).reset_index()
        grouped = grouped.sort_values("_line_total" if "_line_total" in grouped.columns else country_col, ascending=False)

        results = []
        for _, row in grouped.iterrows():
            results.append(GeographicPerformance(
                country=str(row[country_col]),
                revenue=float(row.get("_line_total", 0)),
                order_count=int(row.get(invoice_col, 0)) if invoice_col else 0,
                customer_count=int(row.get(cust_col, 0)) if cust_col else 0,
            ))

        return results

    def calculate_cancellation_stats(self) -> Optional[dict[str, Any]]:
        """Calculate detailed cancellation statistics."""
        invoice_col = self._get_col(self.ROLE_INVOICE)
        if not invoice_col:
            return None

        cancellations = self._get_cancellations()
        if len(cancellations) == 0:
            return {"total_cancellations": 0, "cancellation_revenue_impact": 0.0}

        stats: dict[str, Any] = {
            "total_cancellations": int(cancellations[invoice_col].astype(str).nunique()),
        }

        if "_line_total" in cancellations.columns:
            # Cancelled amounts are typically negative
            stats["cancellation_revenue_impact"] = float(cancellations["_line_total"].sum())

        return stats

    def calculate_full_analytics(self, dataset_id: str) -> AnalyticsResponse:
        """Calculate all analytics for a dataset."""
        return AnalyticsResponse(
            dataset_id=dataset_id,
            summary=self.calculate_summary(dataset_id),
            monthly_revenue=self.calculate_monthly_revenue(),
            top_products=self.calculate_top_products(),
            geographic_performance=self.calculate_geographic_performance(),
            cancellation_stats=self.calculate_cancellation_stats(),
        )
