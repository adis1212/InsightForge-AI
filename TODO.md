# InsightForge AI — Task Tracking & Roadmap

Status Legend:
- [x] **DONE**: Fully implemented, integrated, and verified with automated tests.
- [/] **IN PROGRESS**: Active implementation or verification in progress.
- [ ] **NOT STARTED**: Scheduled for future prompts (Prompts 3–6).
- [!] **BLOCKED**: Blocked by external dependency or awaiting prerequisites.

---

## Stage 1 — Research and Architecture (Verified Complete)
- [x] Inspect workspace and verify development environment tools.
- [x] Formulate comprehensive system architecture ([ARCHITECTURE.md](file:///d:/Insightforge/ARCHITECTURE.md)).
- [x] Define product specifications and persona friction points ([PROJECT_SPEC.md](file:///d:/Insightforge/PROJECT_SPEC.md)).
- [x] Record architectural decision records ADRs 001–009 ([DECISIONS.md](file:///d:/Insightforge/DECISIONS.md)).
- [x] Author academic evaluation methodology and rubrics ([EVALUATION.md](file:///d:/Insightforge/EVALUATION.md)).
- [x] Author comprehensive testing strategy ([TESTING.md](file:///d:/Insightforge/TESTING.md)).
- [x] Create project documentation and setup guide ([README.md](file:///d:/Insightforge/README.md)).

## Stage 2 — Full-Stack Foundation (Verified Complete)
- [x] Backend directory structure & FastAPI modular architecture.
- [x] Database configuration with SQLAlchemy 2.0 (PostgreSQL pool + SQLite dialect awareness).
- [x] Alembic migration configuration and environment setup.
- [x] User and Workspace models with multi-tenant relational schema.
- [x] Password hashing using direct native bcrypt with 72-byte truncation boundary.
- [x] JWT token authentication with HMAC-SHA256 signature and expiry claims.
- [x] Workspace-scoped authorization dependencies and role checks (`_check_workspace_access`).
- [x] Consistent global API error handling with custom `InsightForgeException` hierarchy.
- [x] Standardized health check endpoint (`/api/v1/health`).
- [x] Docker Compose definition for PostgreSQL, FastAPI backend, and Vite frontend.
- [x] Backend test suite (42 foundation tests passing).

## Stage 3 — Dataset and Analytics Engine (Verified Complete)
- [x] File upload validator enforcing extensions (`.csv`, `.xlsx`, `.xls`) and 50 MB bound.
- [x] Secure file storage with workspace isolation.
- [x] Tabular file reader supporting CSV and Excel spreadsheets.
- [x] Automatic column role detection via fuzzy pattern matching and string normalization.
- [x] Manual column mapping configuration and override API.
- [x] Comprehensive data quality auditor (missing values, duplicates, dates, cancellations, quality score).
- [x] Reproducible synthetic wholesale dataset generator (5,015 records).
- [x] Deterministic KPI engine in Pandas:
  - [x] Total revenue calculation (strictly excluding cancellation invoices).
  - [x] Unique orders count.
  - [x] Units sold aggregation.
  - [x] Average Order Value (AOV).
  - [x] Unique customer count (excluding NaN values).
  - [x] Cancellation & return rate computation.
  - [x] Monthly revenue timeline with period-over-period growth percentages.
  - [x] Top product ranking by revenue and volume.
  - [x] Geographic market performance aggregation.
  - [x] Division by zero and edge-case guards.
- [x] Strict business rule: profit and margins remain unavailable when reliable costs are missing.
- [x] Expose all analytics through typed FastAPI endpoints.

## Stage 4 — Professional Dashboard (Verified Complete)
- [x] Frontend package setup with React 18, TypeScript, Tailwind CSS, Vite.
- [x] UI Design system: Navy/slate/teal palette, full light and dark mode support.
- [x] Responsive layout with mobile bottom navigation bar and desktop sidebar.
- [x] Page 1: Landing and authentication (`LandingPage.tsx`, `AuthPage.tsx`).
- [x] Page 2: Business workspace management and switcher (`WorkspacePage.tsx`).
- [x] Page 3: Dashboard overview with responsive cards & Recharts area/bar charts (`DashboardOverviewPage.tsx`).
- [x] Page 4: Dataset upload with drag-and-drop & validation (`DatasetUploadPage.tsx`).
- [x] Page 5: Dataset preview, column mapping override & data quality audit (`DatasetPreviewPage.tsx`).
- [x] Page 6: Deep-dive business analytics with geographic & product leaderboards (`AnalyticsPage.tsx`).
- [x] Page 7: Settings with theme preferences & backend health diagnostics (`SettingsPage.tsx`).

## Stage 5 — Evidence-Grounded Prompt Engineering Engine (Verified Complete — Prompt 2)
- [x] LLM Provider Abstraction:
  - [x] `BaseLLMProvider` interface with normalized `LLMResponse`.
  - [x] Deterministic local demo provider (`LocalDeterministicLLMProvider`) requiring zero paid API keys.
  - [x] Real LLM providers: `OpenAILLMProvider`, `GeminiLLMProvider` using `httpx`.
  - [x] Secure API key handling (backend environment only, zero client leakage).
- [x] Three Chained Prompts with Versioning (v1 vs v2 stored Jinja2 templates):
  - [x] Prompt 1: Factual Data Summarization (`prompt1_factual_v1.jinja2`, `prompt1_factual_v2.jinja2`).
  - [x] Prompt 2: Business Insights & Recommendations (`prompt2_insights_v1.jinja2`, `prompt2_insights_v2.jinja2`).
  - [x] Prompt 3: Structured Report Formatting (`prompt3_report_v1.jinja2`, `prompt3_report_v2.jinja2`).
  - [x] Mandatory refusal constraint: "Insufficient data" for unsupported causal factors and profit margins.
  - [x] Absolute constraint: Zero numerical computation by LLM; strictly grounded in Pandas KPIs.
- [x] Deterministic Verification Engine (`VerificationEngine`):
  - [x] Numeric claim verification against metric IDs (`[METRIC:metric_id]`) with 0.5% tolerance.
  - [x] Evidence reference and citation validation.
  - [x] Strict JSON schema validation against Pydantic `ExecutiveCommercialReport`.
  - [x] Detection and reporting of numerical hallucinations and unknown metric IDs.
  - [x] Missing-data handling and refusal verification.
  - [x] Limited auto-repair for markdown fence stripping and ground truth injection.
- [x] Automated Prompt Evaluation Suite:
  - [x] CLI evaluation harness ([evaluate_prompts.py](file:///d:/Insightforge/backend/scripts/evaluate_prompts.py)).
  - [x] Golden test dataset with 4 diverse commercial benchmark scenarios.
  - [x] Controlled empirical comparison of v1 vs v2 (Accuracy, Hallucinations, Schema, Refusal, Latency, Cost).
  - [x] Documented human usefulness rubric.
  - [x] Exported benchmark scorecard ([latest_evaluation_scorecard.json](file:///d:/Insightforge/data/samples/latest_evaluation_scorecard.json)).
- [x] Prompt Studio UI ([PromptStudioPage.tsx](file:///d:/Insightforge/frontend/src/pages/PromptStudioPage.tsx)):
  - [x] Dataset selector and provider engine switcher.
  - [x] Single version execution view (Stage 1 claims, Stage 2 hypotheses/risks, Stage 3 executive brief).
  - [x] Side-by-side A/B comparison view (v1 vs v2 with delta scorecards).
  - [x] Evaluation Lab tab with live scorecard and rubric inspection.
  - [x] Jinja2 template viewer with architectural diff explanations.
- [x] Backend test suite expanded to 57 passing Pytest tests (covering demo mode, security, and integration).
- [x] Zero-cost unauthenticated demo exploration verified end-to-end via automated browser inspection.

## Stage 6 — Machine Learning Intelligence (Verified Complete — Prompt 3)
- [x] Model 1: XGBoost Sales Forecasting Engine ([forecast_service.py](file:///d:/Insightforge/backend/app/services/forecast_service.py)):
  - [x] Historical weekly/monthly sales aggregation strictly excluding cancellations.
  - [x] Leakage-free feature engineering (forward-shifted lags 1..4, rolling mean 3/6, rolling std 3).
  - [x] Calendar and cyclical features (month, quarter, month_sin, month_cos, trend_index).
  - [x] Chronological train/test split (20% holdout test set, zero shuffling).
  - [x] XGBoost regressor training with hyperparameter regularization.
  - [x] Model artifact persistence via Joblib ([xgb_forecast_*.joblib](file:///d:/Insightforge/backend/data/models/)).
  - [x] Seasonal Naive baseline benchmark comparison (Lag-1 persistence).
  - [x] Empirical evaluation metrics (MAE, RMSE, WAPE).
  - [x] Honest outperformance reporting (disclosing when baseline remains competitive).
  - [x] Multi-step recursive forecasting with 95% residual confidence intervals.
  - [x] Insufficient data refusal guard (< 10 time periods).
- [x] Model 2: Isolation Forest Anomaly Detection ([anomaly_service.py](file:///d:/Insightforge/backend/app/services/anomaly_service.py)):
  - [x] Transaction line-item feature engineering (relative price/quantity deviations from SKU medians).
  - [x] Off-hours activity detection and cancellation status flags.
  - [x] Unsupervised Isolation Forest training (100 estimators, 3.0% contamination).
  - [x] Normalized continuous anomaly scoring in [0, 1].
  - [x] Explainable pattern indicators (EXTREME_UNIT_PRICE, UNUSUAL_BULK_QUANTITY, CANCELLATION_SPIKE, OFF_HOURS_ACTIVITY).
  - [x] Four-tier risk severity categorization (Critical, High, Medium, Low).
  - [x] Full source record reference preservation (InvoiceNo, StockCode, CustomerID, Country).
  - [x] Score distribution histogram calculation for dashboard charts.
  - [x] Legal and commercial distinction between statistical outliers and verified fraud.
  - [x] Synthetic anomaly injection test suite (100% empirical recall on injected outliers).
  - [x] Insufficient data refusal guard (< 20 transaction records).
- [x] AI Prompt Integration:
  - [x] Forwarding verified forecast WAPE, horizon projections, and anomaly counts into `prompt2_insights_v2.jinja2`.
  - [x] LLM provider explains ML predictions and risks without inventing numbers.
- [x] Professional ML Intelligence UI ([MLIntelligencePage.tsx](file:///d:/Insightforge/frontend/src/pages/MLIntelligencePage.tsx)):
  - [x] Interactive Recharts Area/Line chart with historical actuals, XGBoost trajectory, naive baseline, and 95% confidence band.
  - [x] Evaluation metric ribbon (WAPE, Baseline WAPE, MAE, RMSE, Verdict).
  - [x] XGBoost feature importance relative gain bar chart.
  - [x] Isolation Forest score distribution histogram.
  - [x] Severity breakdown pills and filter controls.
  - [x] Flagged transaction audit table with search, severity filter, scores, and pattern badges.
  - [x] Comprehensive methodology and legal fraud vs. outlier disclosures tab.
- [x] Backend test suite expanded to **73 passing Pytest tests** (8 forecast tests, 6 anomaly tests, 14 integration tests).

## Stage 7 — Business Document Knowledge Base & Hybrid RAG Retrieval (Verified Complete — Prompt 4)
- [x] Document Ingestion Engine ([retrieval_service.py](file:///d:/Insightforge/backend/app/services/retrieval_service.py)):
  - [x] Multi-format file ingestion supporting PDF and TXT with 25 MB bounded limits.
  - [x] Text extraction using `pypdf` for page-indexed PDF extraction and UTF-8 TXT reader.
  - [x] Prompt injection sanitization neutralizing adversarial patterns (`IGNORE PREVIOUS`, `You are now`, etc.).
  - [x] Sliding-window chunking (400 words per chunk with 60-word overlap) preserving page and chunk references.
- [x] Embedding & Semantic Retrieval:
  - [x] Configurable embedding model using `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dimensional dense vectors).
  - [x] SQLite/PostgreSQL-compatible vector storage (JSON serialized embedding arrays with workspace indexing).
  - [x] In-memory cosine similarity retrieval with minimum similarity threshold floor (0.25).
  - [x] Workspace-scoped multi-tenant isolation guaranteeing zero cross-workspace document leakage.
  - [x] Document deletion cascading to all associated text chunks.
- [x] AI Prompt Engineering Grounding Integration:
  - [x] Context injection into Stage 2 (`prompt2_insights_v2.jinja2`) with document title and source reference citations.
  - [x] Strict rule enforcement: RAG text is evidence, never instructions; zero numerical calculations from retrieved text.
  - [x] Honest refusal: `"Insufficient data"` returned when no relevant business documents are indexed.
- [x] Professional Knowledge Base UI ([KnowledgeBasePage.tsx](file:///d:/Insightforge/frontend/src/pages/KnowledgeBasePage.tsx)):
  - [x] Drag-and-drop document upload with real-time processing indicator.
  - [x] Indexed documents list with file type badges, passage counts, upload timestamps, and delete controls.
  - [x] Semantic search tab with query input, similarity score bars, passage ranking, and citation summaries.
  - [x] RAG Design Rules & Security disclosures tab clarifying tenant isolation and evidence-only boundaries.
  - [x] Navigation links in [Sidebar.tsx](file:///d:/Insightforge/frontend/src/components/layout/Sidebar.tsx) and [BottomNav.tsx](file:///d:/Insightforge/frontend/src/components/layout/BottomNav.tsx).
- [x] Automated Test Suite:
  - [x] 13 dedicated RAG tests in [test_rag.py](file:///d:/Insightforge/backend/app/tests/test_rag.py) (ingestion, retrieval, isolation, similarity floor, cascade delete, injection sanitization, size/type limits, citation provenance).
  - [x] 16 integration tests in [test_api_integration.py](file:///d:/Insightforge/backend/app/tests/test_api_integration.py) including unauthenticated demo knowledge exploration and authenticated CRUD.
  - [x] Backend test suite expanded to **88 passing Pytest tests** (100% pass rate).

## Stage 8 — Controlled Agentic AI Business Analyst (Verified Complete — Prompt 5)
- [x] Controlled LangGraph Business Analysis Agent ([agent_service.py](file:///d:/Insightforge/backend/app/services/agent_service.py)):
  - [x] Stateful `StateGraph` topology with 4 deterministic nodes (`classify_and_plan`, `validate_arguments`, `execute_tools`, `synthesize_response`).
  - [x] Approved Business Analysis Tools (7 tools, zero fake mocks in production):
    - [x] `get_business_kpis` (Pandas deterministic commercial metrics).
    - [x] `analyze_revenue_trends` (Timeline aggregation with growth rates).
    - [x] `get_product_performance` (Catalog revenue and unit rankings).
    - [x] `forecast_sales` (XGBoost time-series forecast with confidence intervals).
    - [x] `detect_anomalies` (Isolation Forest statistical outlier scoring).
    - [x] `retrieve_business_documents` (Sentence-transformers semantic search with cosine ranking).
    - [x] `generate_executive_report` (Three-stage Jinja2 prompt engineering chain).
  - [x] Security Guardrails & Boundary Controls:
    - [x] Zero unrestricted Python execution (`eval`/`exec` strictly forbidden).
    - [x] Zero arbitrary LLM-generated SQL.
    - [x] Zero external system mutations without authorization.
    - [x] Bounded tool executions (maximum 7 tools per turn, bounded periods [1, 12], bounded product limits [1, 20]).
    - [x] Prompt injection defense and immediate refusal for adversarial inputs.
    - [x] Unsupported query fallback for non-commercial queries.
    - [x] Multi-tenant workspace scoping verified on every tool invocation.
- [x] Agent Conversation Persistence ([agent.py](file:///d:/Insightforge/backend/app/models/agent.py)):
  - [x] Relational SQLAlchemy models (`AgentSession`, `AgentMessageRecord`) storing traces, evidences, charts, and intent.
  - [x] Bounded session history endpoints (`/workspaces/{id}/agent/sessions`, `/sessions/{id}`).
- [x] Professional AI Copilot UI ([AICopilotPage.tsx](file:///d:/Insightforge/frontend/src/pages/AICopilotPage.tsx)):
  - [x] Conversational chat interface with role avatars and demo mode badge.
  - [x] Example prompt quick-launcher chips (KPIs, Trends, Forecast, Anomalies, Products, Executive Report).
  - [x] Collapsible Tool Execution Trace drawer detailing parameters, latency in milliseconds, and status badges.
  - [x] Interactive Chart rendering (KPI scorecards, Recharts area trends, horizontal product bar leaderboards, XGBoost forecast with 95% confidence intervals, and anomaly distribution histograms).
  - [x] Clickable evidence citation badges linking metrics and document references.
  - [x] Session switcher and "New Chat" session reset.
  - [x] Responsive layout with desktop sidebar integration and mobile bottom navigation item.
- [x] Automated Test Suite:
  - [x] 13 dedicated agent unit and integration tests in [test_agent.py](file:///d:/Insightforge/backend/app/tests/test_agent.py) covering tool selection, bounds clamping, prompt injection defense, unsupported fallback, full copilot execution, and missing dataset recovery.
  - [x] Full backend regression suite: **101 passed, 0 failures** across all 8 stages.
  - [x] Frontend test suite: **10 passed Vitest tests**; TypeScript type check and production Vite build clean.

## Future Stages (Prompt 6)
- [ ] **Prompt 6:** Final Prompt Engineering Course Evaluation Lab & A/B Benchmark Suite.
