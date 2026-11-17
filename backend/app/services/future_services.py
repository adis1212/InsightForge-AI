"""Future service interfaces for Prompts 5+.

Prompts 1, 2, 3, 4, and 5 implemented:
- AnalyticsService (Pandas deterministic KPIs)
- LLMProvider & PromptService (Evidence-grounded 3-stage prompt engine)
- ForecastService (XGBoost Sales Forecasting, Prompt 3)
- AnomalyService (Isolation Forest Anomaly Detection, Prompt 3)
- RetrievalService (Workspace-scoped RAG with sentence-transformers, Prompt 4)
- AgentService (Controlled LangGraph Business Analysis Copilot, Prompt 5)

Remaining future services return explicit 'not implemented' responses:
- ReportService (PDF Generator, Prompt 5/6)
"""
from typing import Any
from app.services.llm_provider import get_llm_provider, BaseLLMProvider  # noqa: F401
from app.services.prompt_service import prompt_service  # noqa: F401
from app.services.forecast_service import forecast_service, ForecastService  # noqa: F401
from app.services.anomaly_service import anomaly_service, AnomalyService  # noqa: F401
from app.services.retrieval_service import retrieval_service, RetrievalService  # noqa: F401
from app.services.agent_service import agent_service, AgentService  # noqa: F401


from app.services.report_service import report_service, ReportService  # noqa: F401

