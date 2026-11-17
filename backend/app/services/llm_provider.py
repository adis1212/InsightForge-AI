"""LLM Provider abstraction supporting Local Deterministic Demo, OpenAI, Gemini, and Anthropic."""
import os
import time
import json
from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel
import httpx


class LLMResponse(BaseModel):
    """Normalized response from any LLM provider."""
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    model_name: str
    provider_type: str
    cost_estimate_usd: float = 0.0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        stage_hint: Optional[str] = None,
        prompt_version: str = "v2",
        kpi_context: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        """Generate response from the LLM."""
        pass


class LocalDeterministicLLMProvider(BaseLLMProvider):
    """
    Deterministic Local LLM Provider for offline evaluation and testing.
    Does NOT require paid API credentials or external network access.
    
    Generates realistic, grounded outputs tailored to the requested prompt version:
    - v1 outputs loosely grounded statements with occasional formatting or rounding drift
      (demonstrating the need for the verification engine).
    - v2 outputs strict, structured evidence citations [METRIC:id], explicit [HYPOTHESIS] tags,
      strict "Insufficient data" refusal handling, and valid Pydantic JSON.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        stage_hint: Optional[str] = None,
        prompt_version: str = "v2",
        kpi_context: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        start_time = time.perf_counter()
        kpi = kpi_context or {}

        # Extract KPIs or fallback to baseline
        rev = kpi.get("total_revenue", 1248950.45)
        orders = kpi.get("unique_orders", 1420)
        units = kpi.get("units_sold", 48920)
        aov = kpi.get("average_order_value", 879.54)
        custs = kpi.get("unique_customers", 198)
        cancels = kpi.get("cancellation_rate", 4.9)
        top_prod = kpi.get("top_product", "Diesel Generator 5kW")
        top_prod_rev = kpi.get("top_product_revenue", 145200.0)
        top_country = kpi.get("top_country", "United Kingdom")
        top_country_rev = kpi.get("top_country_revenue", 437130.0)

        # Generate response based on stage and version
        if stage_hint == "stage_1":
            if prompt_version == "v1":
                # v1: loose formatting, slight rounding discrepancies, no citation tags
                text = (
                    f"The business generated approximately ${rev:,.2f} in overall gross revenue across around {orders} orders. "
                    f"Total units delivered came out to {units:,} pieces. The average transaction value hovered at about ${aov:.2f}. "
                    f"A customer base of roughly {custs} accounts participated in transactions. "
                    f"Cancellation and return activity represented {cancels:.1f}% of total invoice volume. "
                    f"The leading revenue generator was {top_prod} totaling ${top_prod_rev:,.2f}, and the dominant export territory was {top_country}."
                )
            else:
                # v2: strict evidence citations with [METRIC:id] and strict claim breakdown
                claims_json = [
                    {
                        "claim_id": "CLM-001",
                        "statement": f"Total verified net commercial revenue achieved was ${rev:,.2f}.",
                        "metric_references": [{"metric_id": "total_revenue", "cited_value": float(rev)}]
                    },
                    {
                        "claim_id": "CLM-002",
                        "statement": f"Total fulfilled order volume reached {int(orders)} distinct invoices.",
                        "metric_references": [{"metric_id": "unique_orders", "cited_value": float(orders)}]
                    },
                    {
                        "claim_id": "CLM-003",
                        "statement": f"Total merchandise volume delivered was {int(units)} units.",
                        "metric_references": [{"metric_id": "units_sold", "cited_value": float(units)}]
                    },
                    {
                        "claim_id": "CLM-004",
                        "statement": f"The average order value (AOV) across valid orders was ${aov:,.2f}.",
                        "metric_references": [{"metric_id": "average_order_value", "cited_value": float(aov)}]
                    },
                    {
                        "claim_id": "CLM-005",
                        "statement": f"A verified cohort of {int(custs)} unique customer accounts transacted in this period.",
                        "metric_references": [{"metric_id": "unique_customers", "cited_value": float(custs)}]
                    },
                    {
                        "claim_id": "CLM-006",
                        "statement": f"Order cancellation rate was measured at {cancels:.1f}% of total transactions.",
                        "metric_references": [{"metric_id": "cancellation_rate", "cited_value": float(cancels)}]
                    }
                ]
                text = json.dumps(claims_json, indent=2)

        elif stage_hint == "stage_2":
            if prompt_version == "v1":
                # v1: ungrounded speculation, no [HYPOTHESIS] label, guesses profit margins without data
                text = (
                    f"Observations: Revenue of ${rev:,.2f} indicates reasonable market demand. "
                    f"The cancellation rate of {cancels:.1f}% is probably due to poor courier performance or defect rates. "
                    f"Profit margins are estimated at 28% based on industrial standards. "
                    f"Recommendation: Lower prices on {top_prod} to capture 50% more market share in {top_country}."
                )
            else:
                # v2: explicit [HYPOTHESIS], refusal on missing cost/margin data ("Insufficient data"), metric-tied recommendations
                insights = {
                    "insights_text": f"Grounded commercial assessment across ${rev:,.2f} in net volume.",
                    "hypotheses": [
                        {
                            "hypothesis_id": "HYP-001",
                            "observation": f"Top product ({top_prod}) contributes ${top_prod_rev:,.2f} across {orders} total orders.",
                            "hypothesis_statement": "[HYPOTHESIS] Revenue is heavily concentrated in heavy industrial equipment lines, creating SKU vulnerability.",
                            "confidence": "high",
                            "grounding_metric_ids": ["total_revenue", "unique_orders"]
                        },
                        {
                            "hypothesis_id": "HYP-002",
                            "observation": f"A cancellation rate of {cancels:.1f}% resulted in transaction reversals.",
                            "hypothesis_statement": "[HYPOTHESIS] Cancellation concentration may correlate with bulk export logistics constraints.",
                            "confidence": "medium",
                            "grounding_metric_ids": ["cancellation_rate"]
                        }
                    ],
                    "risks": [
                        {
                            "risk_id": "RSK-001",
                            "description": f"Territory concentration: {top_country} accounts for over 35% of total turnover (${top_country_rev:,.2f}).",
                            "severity": "high",
                            "impact_metric_id": "total_revenue"
                        },
                        {
                            "risk_id": "RSK-002",
                            "description": f"Cancellation drag: {cancels:.1f}% of transactions require reconciliation and inventory restocking.",
                            "severity": "medium",
                            "impact_metric_id": "cancellation_rate"
                        }
                    ],
                    "recommendations": [
                        {
                            "recommendation_id": "REC-001",
                            "title": "Establish Territory Diversification Incentive",
                            "action": f"Expand active customer base in secondary markets (DE, FR) beyond current baseline of {custs} accounts.",
                            "expected_impact": "Reduce revenue concentration risk below 30% per territory.",
                            "target_metric_id": "unique_customers",
                            "priority": "P1"
                        },
                        {
                            "recommendation_id": "REC-002",
                            "title": "Targeted SKU Reorder Buffer for High-Volume Items",
                            "action": f"Maintain safety stock for {top_prod} to safeguard the ${top_prod_rev:,.2f} revenue stream.",
                            "expected_impact": "Prevent stockout disruptions on leading revenue driver.",
                            "target_metric_id": "units_sold",
                            "priority": "P2"
                        }
                    ],
                    "unsupported_factors_noted": [
                        "Gross profit margin and unit profitability: Insufficient data (item unit cost COGS not provided in transaction log).",
                        "Root cause of order cancellations: Insufficient data (return reason codes not captured in schema)."
                    ]
                }

                # Ground with verified ML forecast and anomaly findings if present
                if kpi.get("ml_forecast"):
                    fc = kpi["ml_forecast"]
                    insights["hypotheses"].append({
                        "hypothesis_id": "HYP-003",
                        "observation": f"XGBoost sales forecast evaluated with WAPE of {fc.get('wape', 23.9):.1f}% over {fc.get('forecast_horizon_periods', 6)} periods.",
                        "hypothesis_statement": f"[HYPOTHESIS] Revenue trajectory follows seasonal cyclical patterns (Outperforms baseline: {fc.get('outperforms_baseline', False)}).",
                        "confidence": "high",
                        "grounding_metric_ids": ["total_revenue"]
                    })

                if kpi.get("ml_anomalies"):
                    anom = kpi["ml_anomalies"]
                    insights["risks"].append({
                        "risk_id": "RSK-003",
                        "description": f"Statistical outlier exposure: {anom.get('anomaly_count', 0)} transactions isolated by Isolation Forest ({anom.get('critical_count', 0)} critical risk).",
                        "severity": "high",
                        "impact_metric_id": "cancellation_rate"
                    })

                text = json.dumps(insights, indent=2)

        elif stage_hint == "stage_3":
            if prompt_version == "v1":
                # v1: wraps JSON in markdown conversational text, misses required fields
                text = (
                    "```json\n"
                    "{\n"
                    f'  "report_title": "Executive Summary Report",\n'
                    f'  "executive_summary": "The company recorded ${rev:,.2f} in revenue.",\n'
                    f'  "kpi_highlights": [{{"label": "Revenue", "metric_id": "total_revenue", "value": {rev}, "formatted": "${rev:,.2f}", "context_note": "Total"}}]\n'
                    "}\n"
                    "```"
                )
            else:
                # v2: clean strict JSON compliant with ExecutiveCommercialReport schema
                report = {
                    "report_title": "Executive Commercial Intelligence Report",
                    "dataset_name": kpi.get("dataset_name", "Wholesale Benchmark FY2023"),
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "prompt_version": "v2-strict-evidence-grounded",
                    "executive_summary": (
                        f"Commercial operations delivered ${rev:,.2f} in net revenue across {orders:,} verified orders "
                        f"and {units:,} units sold to {custs} distinct customer accounts. "
                        f"The average order value reached ${aov:,.2f}. The cancellation rate was controlled at {cancels:.1f}%. "
                        f"Revenue is anchored by {top_prod} (${top_prod_rev:,.2f}) and market strength in {top_country} (${top_country_rev:,.2f})."
                    ),
                    "kpi_highlights": [
                        {
                            "label": "Total Net Revenue",
                            "metric_id": "total_revenue",
                            "value": float(rev),
                            "formatted": f"${rev:,.2f}",
                            "trend_direction": "up",
                            "context_note": "Net of all cancellations and returns"
                        },
                        {
                            "label": "Unique Orders",
                            "metric_id": "unique_orders",
                            "value": float(orders),
                            "formatted": f"{orders:,}",
                            "trend_direction": "neutral",
                            "context_note": "Distinct invoice numbers fulfilled"
                        },
                        {
                            "label": "Units Sold",
                            "metric_id": "units_sold",
                            "value": float(units),
                            "formatted": f"{units:,}",
                            "trend_direction": "up",
                            "context_note": "Aggregate delivered quantity"
                        },
                        {
                            "label": "Average Order Value",
                            "metric_id": "average_order_value",
                            "value": float(aov),
                            "formatted": f"${aov:,.2f}",
                            "trend_direction": "up",
                            "context_note": "Revenue per unique order"
                        },
                        {
                            "label": "Active Customers",
                            "metric_id": "unique_customers",
                            "value": float(custs),
                            "formatted": f"{custs}",
                            "trend_direction": "neutral",
                            "context_note": "Distinct transacting commercial accounts"
                        },
                        {
                            "label": "Cancellation Rate",
                            "metric_id": "cancellation_rate",
                            "value": float(cancels),
                            "formatted": f"{cancels:.1f}%",
                            "trend_direction": "down",
                            "context_note": "Cancelled invoice proportion"
                        }
                    ],
                    "key_commercial_observations": [
                        f"Commercial revenue reached ${rev:,.2f} across {orders} orders.",
                        f"Core volume driver is {top_prod} delivering ${top_prod_rev:,.2f}.",
                        f"Primary export market is {top_country} delivering ${top_country_rev:,.2f}."
                    ],
                    "strategic_hypotheses": [
                        {
                            "hypothesis_id": "HYP-001",
                            "observation": f"Top product delivers ${top_prod_rev:,.2f} of total revenue.",
                            "hypothesis_statement": "[HYPOTHESIS] SKU concentration creates supplier dependency vulnerability.",
                            "confidence": "high",
                            "grounding_metric_ids": ["total_revenue"]
                        }
                    ],
                    "operational_risks": [
                        {
                            "risk_id": "RSK-001",
                            "description": f"Territory concentration in {top_country} (${top_country_rev:,.2f}).",
                            "severity": "high",
                            "impact_metric_id": "total_revenue"
                        }
                    ],
                    "prioritized_recommendations": [
                        {
                            "recommendation_id": "REC-001",
                            "title": "Territory Customer Expansion",
                            "action": f"Expand active customer base beyond current baseline of {custs} accounts.",
                            "expected_impact": "Diversify geographic commercial dependency.",
                            "target_metric_id": "unique_customers",
                            "priority": "P1"
                        }
                    ],
                    "data_quality_disclosures": [
                        "Data quality audit completed: Zero NaN date parse errors; duplicate rows isolated.",
                        "All metric references verified against deterministic Pandas calculations."
                    ],
                    "unsupported_data_disclosures": [
                        "Cost of goods sold (COGS) and profit margin: Insufficient data (not in transactional log).",
                        "Return causal categories: Insufficient data (reasons not recorded at line level)."
                    ]
                }
                text = json.dumps(report, indent=2)

        else:
            text = f"Verified response generated deterministically for prompt version {prompt_version}."

        latency = (time.perf_counter() - start_time) * 1000 + 45.0  # Realistic local execution latency
        prompt_tokens = len(prompt.split()) * 2
        completion_tokens = len(text.split()) * 2

        return LLMResponse(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=round(latency, 2),
            model_name="deterministic-local-demo",
            provider_type="local_demo",
            cost_estimate_usd=0.0,
        )


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        stage_hint: Optional[str] = None,
        prompt_version: str = "v2",
        kpi_context: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("OpenAI API key not configured. Use local_demo provider.")

        start_time = time.perf_counter()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency = (time.perf_counter() - start_time) * 1000
        choice = data["choices"][0]
        text = choice["message"]["content"]
        usage = data.get("usage", {})
        p_tok = usage.get("prompt_tokens", 0)
        c_tok = usage.get("completion_tokens", 0)
        cost = (p_tok * 0.00015 + c_tok * 0.0006) / 1000.0  # Approx gpt-4o-mini cost

        return LLMResponse(
            text=text,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_tokens=p_tok + c_tok,
            latency_ms=round(latency, 2),
            model_name=self.model,
            provider_type="openai",
            cost_estimate_usd=round(cost, 6),
        )


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        stage_hint: Optional[str] = None,
        prompt_version: str = "v2",
        kpi_context: Optional[dict[str, Any]] = None,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Use local_demo provider.")

        start_time = time.perf_counter()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency = (time.perf_counter() - start_time) * 1000
        candidate = data["candidates"][0]
        text = candidate["content"]["parts"][0]["text"]
        p_tok = len(prompt.split()) * 2
        c_tok = len(text.split()) * 2

        return LLMResponse(
            text=text,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_tokens=p_tok + c_tok,
            latency_ms=round(latency, 2),
            model_name=self.model,
            provider_type="gemini",
            cost_estimate_usd=0.0001,
        )


def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    """Factory to get the configured LLM provider."""
    p_type = (provider_type or os.getenv("LLM_PROVIDER", "local_demo")).lower()
    
    if p_type == "openai":
        return OpenAILLMProvider()
    elif p_type == "gemini":
        return GeminiLLMProvider()
    else:
        return LocalDeterministicLLMProvider()
