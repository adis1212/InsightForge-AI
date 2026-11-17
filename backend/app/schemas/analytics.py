"""Pydantic schemas for analytics KPIs."""
from pydantic import BaseModel
from typing import Optional, Any


class KPIValue(BaseModel):
    """Single KPI value."""
    name: str
    value: Optional[float] = None
    formatted: str = ""
    description: str = ""
    available: bool = True
    unavailable_reason: Optional[str] = None


class KPISummary(BaseModel):
    """Overview KPI summary."""
    dataset_id: str
    total_revenue: KPIValue
    unique_orders: KPIValue
    units_sold: KPIValue
    average_order_value: KPIValue
    unique_customers: KPIValue
    cancellation_rate: KPIValue


class RevenueGrowth(BaseModel):
    """Monthly revenue growth."""
    period: str
    revenue: float
    growth_rate: Optional[float] = None


class ProductRanking(BaseModel):
    """Product ranking by revenue."""
    rank: int
    stock_code: str
    description: str
    total_revenue: float
    units_sold: int


class GeographicPerformance(BaseModel):
    """Geographic performance."""
    country: str
    revenue: float
    order_count: int
    customer_count: int


class AnalyticsResponse(BaseModel):
    """Full analytics response."""
    dataset_id: str
    summary: KPISummary
    monthly_revenue: list[RevenueGrowth] = []
    top_products: list[ProductRanking] = []
    geographic_performance: list[GeographicPerformance] = []
    cancellation_stats: Optional[dict[str, Any]] = None
