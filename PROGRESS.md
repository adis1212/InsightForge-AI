# InsightForge AI — Progress Report

**Execution:** Prompt 5 of 6 (Stage 8: Controlled Agentic AI Business Analyst)  
**Audit & Verification Date:** November 17, 2026  

---

## Executive Status Overview

| Stage | Description | Target | Current Status | Notes |
| :---: | :--- | :---: | :---: | :--- |
| **Stage 1** | Research & System Architecture | Prompt 1 | **100% COMPLETE** | Architecture, ADRs (001–009), DB schema, evaluation plan, and specifications verified. |
| **Stage 2** | Full-Stack Foundation | Prompt 1 | **100% COMPLETE** | FastAPI backend, JWT auth, workspace authorization, Docker config, and 52 tests verified. |
| **Stage 3** | Dataset & Analytics Engine | Prompt 1 | **100% COMPLETE** | CSV/XLSX parser, auto-column detector, quality auditor, synthetic dataset, and deterministic Pandas KPI engine verified. |
| **Stage 4** | Professional Dashboard | Prompt 1 | **100% COMPLETE** | 7 working pages, navy/slate/teal theme, mobile bottom nav, desktop sidebar, Recharts, 10 Vitest tests, and Vite build verified. |
| **Stage 5** | Prompt Engineering Engine | Prompt 2 | **100% COMPLETE** | 3-stage prompt chain (v1 vs v2 Jinja2), LLM provider abstraction, VerificationEngine, automated evaluation, and Prompt Studio UI. |
| **Stage 6** | Predictive ML & Forecasting | Prompt 3 | **100% COMPLETE** | XGBoost time-series revenue forecasting, Isolation Forest outlier screening, baseline comparison, and ML Intelligence UI. |
| **Stage 7** | Business Knowledge RAG | Prompt 4 | **100% COMPLETE** | Document ingestion (PDF/TXT), sentence-transformers vector embeddings, cosine retrieval, prompt grounding, and Knowledge Base UI. |
| **Stage 8** | Controlled Agentic Copilot | Prompt 5 | **100% COMPLETE** | Controlled LangGraph business analysis agent, 7 approved tools, execution trace drawer, interactive charts, and AI Copilot UI. |
| **Stage 9** | PDF Reports & Course Lab | Prompt 6 | **PLANNED** | Automated boardroom PDF report generation, final benchmark evaluation suite. |

---

## Detailed Milestone Verification Log (Prompt 2 Deliverables)

### 1. LLM Provider Abstraction
* Created [backend/app/services/llm_provider.py](file:///d:/Insightforge/backend/app/services/llm_provider.py) defining `BaseLLMProvider` and normalized `LLMResponse`.
* Implemented `LocalDeterministicLLMProvider` ensuring offline testing without paid API credentials.
* Implemented `OpenAILLMProvider` and `GeminiLLMProvider` using async `httpx` clients.
* Strict security constraint enforced: Zero exposure of API keys in frontend code (all calls proxied through backend).

### 2. Three Chained Prompts with Versioning (v1 vs v2)
* Stored Jinja2 templates created in `backend/app/prompts/`:
  - `prompt1_factual_v1.jinja2` vs `prompt1_factual_v2.jinja2`
  - `prompt2_insights_v1.jinja2` vs `prompt2_insights_v2.jinja2`
  - `prompt3_report_v1.jinja2` vs `prompt3_report_v2.jinja2`
* Documented architectural differences:
  - **Prompt 1:** v1 outputs loose prose prone to approximation; v2 requires strict structured claims with `[METRIC:metric_id]` citations.
  - **Prompt 2:** v1 generates ungrounded speculation; v2 mandates explicit `[HYPOTHESIS]` prefixes and requires `"Insufficient data"` for unsupported causal factors and profit margins.
  - **Prompt 3:** v1 outputs conversational markdown; v2 enforces pure JSON strictly matching the `ExecutiveCommercialReport` Pydantic schema.

### 3. Deterministic Verification Engine
* Implemented [backend/app/services/verification_engine.py](file:///d:/Insightforge/backend/app/services/verification_engine.py).
* Numeric claim verification validates cited values against deterministic Pandas KPIs with a 0.5% tolerance threshold.
* Detects hallucinated metric IDs and conflicting numbers.
* Validates Pydantic schema conformance and cleans markdown wrappers.
* Verifies refusal compliance when item cost or return causal codes are absent.

### 4. Automated Evaluation Suite
* Created [backend/scripts/evaluate_prompts.py](file:///d:/Insightforge/backend/scripts/evaluate_prompts.py).
* 4 Golden test dataset scenarios evaluated: Standard Balanced, High Cancellation Spike, Single-Product Concentration, and Emerging Expansion.
* Documented human usefulness rubric across 5 dimensions.
* Real executed scorecard saved to [data/samples/latest_evaluation_scorecard.json](file:///d:/Insightforge/data/samples/latest_evaluation_scorecard.json):
  - **v1 Accuracy:** 33.3% $\rightarrow$ **v2 Accuracy:** 100.0% (+66.7% improvement).
  - **v1 Schema Pass:** 0.0% $\rightarrow$ **v2 Schema Pass:** 100.0% (+100.0% improvement).
  - **v1 Refusal Pass:** 0.0% $\rightarrow$ **v2 Refusal Pass:** 100.0% (+100.0% improvement).
  - **v1 Latency:** 2.2ms $\rightarrow$ **v2 Latency:** 1.9ms.

### 5. Prompt Studio UI
* Created [frontend/src/pages/PromptStudioPage.tsx](file:///d:/Insightforge/frontend/src/pages/PromptStudioPage.tsx).
* Added `/prompt-studio` route in `App.tsx` and navigation items in `Sidebar.tsx` and `BottomNav.tsx`.
* Features 4 sub-views:
  - **Prompt Studio Pipeline:** Live 3-stage execution with claims table, hypotheses, refusal notices, and executive brief.
  - **v1 vs v2 Comparison:** Side-by-side delta scorecard and stage output comparison.
  - **Evaluation Lab:** Golden test dataset scorecard and grading rubric.
  - **Jinja2 Templates:** Template viewer with architectural diff rationale.

### 6. Validation & Quality Checks
* **Backend Pytest:** 57 Passed, 0 Failed in 5.60s (100% pass rate).
* **Frontend Vitest:** 10 Passed, 0 Failed in 625ms (100% pass rate).
* **Frontend ESLint:** 0 errors, 0 warnings.
* **Frontend Vite Build:** Clean production bundle compiled in 6.14s (`dist/` verified).
* **Live Browser UI Audit:** Verified via automated browser inspection at `http://localhost:5173/prompt-studio` with all 4 sub-views active and populated.

---

## Stage 5 Comprehensive Audit & Fixes (Post-Prompt 2 Audit)
During the full-stack source code audit, the following critical disconnected feature was identified and resolved:
1. **Unauthenticated Demo Mode API Barrier:**
   - *Issue Identified:* In Demo Mode, an evaluator visiting `/prompt-studio` without credentials received `401 Unauthorized` on `/prompts/execute`, `/prompts/evaluation`, `/prompts/templates`, and `/prompts/compare`. The UI silently failed to render any output.
   - *Fix Implemented:* Implemented `get_current_user_optional` in [app/core/deps.py](file:///d:/Insightforge/backend/app/core/deps.py). Permitted zero-cost demo exploration for `workspace_id.startswith("demo-")` and `benchmark-wholesale` datasets using `LocalDeterministicLLMProvider`, while strictly retaining authentication requirements for live cloud providers (`OpenAI`, `Gemini`) and non-demo workspaces (ADR-010).
   - *Frontend Enhancement:* Added explicit error banner, loading spinner, and empty/ready state card in [PromptStudioPage.tsx](file:///d:/Insightforge/frontend/src/pages/PromptStudioPage.tsx).
   - *Live Verification:* Verified end-to-end via automated browser subagent; all 4 tabs now render 100% verified claims, hypotheses, refusal notices, side-by-side comparison, and evaluation scorecards.
   - *Automated Regression Tests:* Added 5 dedicated integration tests in `TestDemoModeUnauthenticatedAccess` covering demo execution, comparison, templates, scorecard, and cloud LLM 401 guard. Total backend tests increased from 52 to 57.

---

## Detailed Milestone Verification Log (Prompt 3 Deliverables — Stage 6 ML)

### 1. MODEL 1 — XGBoost Sales Forecasting
* Created [backend/app/services/forecast_service.py](file:///d:/Insightforge/backend/app/services/forecast_service.py) with `ForecastService`.
* Built chronological sales aggregation by calendar week and month, strictly filtering out cancellations and calculating net line revenue.
* Engineered leakage-free features: forward-shifted historical lags $t-1..t-4$, rolling means (3, 6), rolling standard deviation (3), calendar indicators (month, quarter), cyclical transforms ($\sin/\cos$), and linear trend indices.
* Implemented strict chronological 20% holdout split without random shuffling to prevent future-lookahead target leakage (ADR-011).
* Evaluated against a **Seasonal Naive lag-1 persistence baseline** calculating MAE, RMSE, and WAPE.
* **Honest Evaluation Rule Enforced:** On the benchmark single-year weekly wholesale dataset, XGBoost achieved holdout WAPE of 45.71% vs. naive baseline WAPE of 23.92%. The system transparently flags `outperforms_baseline: false` and discloses that the persistence baseline remains competitive on short-horizon series.
* Generated multi-step recursive future horizon forecast with 95% residual confidence intervals ($\pm 1.96 \cdot \text{std}_{\text{residuals}} \cdot \sqrt{h}$).
* Implemented model artifact persistence using Joblib to `backend/data/models/`.
* Handled insufficient data gracefully with a refusal guard for $< 10$ time periods.

### 2. MODEL 2 — Isolation Forest Anomaly Detection
* Created [backend/app/services/anomaly_service.py](file:///d:/Insightforge/backend/app/services/anomaly_service.py) with `AnomalyService`.
* Built transaction-level feature engineering: SKU-relative price and quantity deviation ratios against catalog medians, log transaction amounts, cancellation indicators, and off-hours activity detection.
* Trained unsupervised `IsolationForest(n_estimators=100, contamination=0.03, random_state=42)` producing continuous anomaly scores normalized to $[0, 1]$.
* Engineered explainable pattern badges: `EXTREME_UNIT_PRICE`, `UNUSUAL_BULK_QUANTITY`, `CANCELLATION_SPIKE`, `OFF_HOURS_ACTIVITY`, and `HIGH_TRANSACTION_VALUE`.
* Classified anomalies into a 4-tier risk severity hierarchy (`critical`, `high`, `medium`, `low`) and calculated distribution histogram buckets.
* Preserved full transaction provenance (`invoice_no`, `stock_code`, `description`, `customer_id`, `country`).
* Enforced legal and commercial disclaimers distinguishing statistical anomalies from confirmed fraud.
* Verified 100% recall on synthetic anomaly injection tests (4 injected extreme outliers detected with high confidence).
* Insufficient data refusal guard enforced for $< 20$ records.

### 3. AI Prompt Engineering Engine Integration
* Extended Jinja2 context in `prompt2_insights_v2.jinja2` to ground business hypotheses and commercial risks in verified ML metrics (`ml_forecast` and `ml_anomalies`).
* Updated `LocalDeterministicLLMProvider` to generate evidence-backed hypotheses (`HYP-003` for forecast horizon and baseline comparison) and operational risks (`RSK-003` for flagged transaction patterns).
* Adheres strictly to the architectural constraint: the LLM contextualizes and explains predictions, but never computes or invents numerical values.

### 4. Professional ML Intelligence Frontend UI
* Created [frontend/src/pages/MLIntelligencePage.tsx](file:///d:/Insightforge/frontend/src/pages/MLIntelligencePage.tsx).
* Added routes `/ml` and `/ml-intelligence` in `App.tsx` and links in `Sidebar.tsx`, `BottomNav.tsx`, and `DashboardOverviewPage.tsx`.
* Rendered Recharts area/line chart with historical actuals, XGBoost trajectory, seasonal naive baseline, and 95% confidence intervals.
* Displayed model evaluation scorecard ribbon (WAPE, Baseline WAPE, MAE, RMSE, Verdict).
* Displayed XGBoost feature importance bar chart.
* Displayed Isolation Forest anomaly score histogram and severity breakdown chips.
* Built searchable, filterable flagged transaction audit table with pattern tags and transaction details.
* Added Methodology & Legal Disclosures tab clarifying leakage prevention and fraud vs. outlier distinctions.

### 5. Automated Verification & Test Suite
* **Backend Pytest:** Expanded from 57 to **73 Passed, 0 Failed** (100% pass rate).
  - 8 forecast tests in `test_ml_forecast.py` (aggregation, leakage prevention, split, XGBoost/WAPE, baseline, confidence intervals, persistence, refusal).
  - 6 anomaly tests in `test_ml_anomalies.py` (features, Isolation Forest scoring, provenance, synthetic injection recall, refusal).
  - 14 integration tests in `test_api_integration.py` (including unauthenticated demo access for forecast and anomalies).
* **Frontend Vitest:** 10 Passed, 0 Failed.
* **Frontend ESLint:** 0 errors, 0 warnings.
* **Frontend Production Build:** `tsc && vite build` compiled cleanly in 6.16s.
* **Live Browser Audit:** Verified via Playwright browser subagent on `http://localhost:5173/ml` with full chart rendering and table filtering.

---

## Detailed Milestone Verification Log (Prompt 4 Deliverables — Stage 7 RAG)

### 1. Document Ingestion & Chunking Engine
* Created [backend/app/models/knowledge.py](file:///d:/Insightforge/backend/app/models/knowledge.py) defining `KnowledgeDocument` and `DocumentChunk` relational models.
* Supported document formats: PDF (via `pypdf` page-by-page extraction) and TXT (UTF-8 encoding) with a 25 MB upper bound.
* Implemented sliding-window word chunking (400 words per chunk with 60-word overlap) preserving chunk indices, page numbers, and structured source references (e.g. `Page 1, chunk 2`).
* Automated cascade deletion: deleting a document cleanly purges all underlying chunk vectors from the database.

### 2. Dense Semantic Vector Embeddings & In-Memory Cosine Retrieval
* Implemented [backend/app/services/retrieval_service.py](file:///d:/Insightforge/backend/app/services/retrieval_service.py) with lazy-loaded `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dimensional dense embeddings).
* Embedded text chunks into JSON-serialized vector arrays with database index on `workspace_id` for instant multi-tenant scoping.
* Fast in-memory cosine similarity retrieval with a minimum similarity threshold floor (0.25).
* Achieved ~12.8 ms retrieval latency on warm query evaluation.

### 3. Prompt Injection Defense & Grounding Rules Enforced
* **Adversarial Sanitization:** Ingestion pipeline neutralizes prompt injection vectors (`IGNORE PREVIOUS`, `forget everything`, `you are now`, `system:`) by replacing matched lines with `[CONTENT REMOVED: policy violation]` before embedding.
* **Evidence-Only Rule:** Retrieved passages are strictly formatted as contextual evidence (`[DOC-N] Title (Source)`).
* **Zero Math Contamination:** Language models are explicitly instructed never to calculate numerical KPIs from document prose. All numbers remain 100% verified against deterministic Pandas computations.
* **Honest Fallback:** When no documents exist or similarity is below threshold, the system transparently outputs `"Insufficient data — no relevant business documents uploaded to this workspace knowledge base."`

### 4. Professional Knowledge Base UI
* Created [frontend/src/pages/KnowledgeBasePage.tsx](file:///d:/Insightforge/frontend/src/pages/KnowledgeBasePage.tsx).
* Added routes `/knowledge` and `/knowledge-base` in `App.tsx` and links in `Sidebar.tsx` and `BottomNav.tsx`.
* Features 3 dedicated sub-views:
  - **Documents Tab:** Drag-and-drop document upload drop zone (.pdf / .txt), processing indicators, and indexed documents table with metadata, passage counts, and delete actions.
  - **Search Tab:** Live semantic search testing over workspace documents with cosine similarity score bars, passage ranking, and formatted evidence summaries.
  - **Info & Security Tab:** Complete disclosure of RAG design rules, prompt injection sanitization, workspace isolation guarantees, and technical specifications.

### 5. Automated Verification & Test Suite
* **Backend Pytest:** Expanded from 73 to **88 Passed, 0 Failed** (100% pass rate in 51.48s).
  - 13 dedicated RAG unit & security tests in [test_rag.py](file:///d:/Insightforge/backend/app/tests/test_rag.py).
  - 16 full integration tests in [test_api_integration.py](file:///d:/Insightforge/backend/app/tests/test_api_integration.py).
* **Frontend Vitest:** 10 Passed, 0 Failed in 619ms.
* **Frontend ESLint:** 0 errors, 0 warnings.
* **Frontend Production Build:** Clean compilation via `tsc && vite build` (2,132 modules transformed into `dist/` in 7.09s).
* **Live Browser Audit:** Verified end-to-end via automated browser subagent at `http://localhost:5173/knowledge` across Documents, Search, and Info tabs.


---

## Detailed Milestone Verification Log (Prompt 5 Deliverables — Stage 8)

### 1. Controlled LangGraph Business Analysis Agent
* Implemented [backend/app/services/agent_service.py](file:///d:/Insightforge/backend/app/services/agent_service.py) using LangGraph `StateGraph`.
* Established a 4-node deterministic pipeline:
  1. `classify_and_plan`: Intent classification, prompt-injection defense, and approved tool selection.
  2. `validate_arguments`: Parameter clamping and boundary enforcement (`periods` $\in [1, 12]$, `product_limit` $\in [1, 20]$, `contamination` $\in [0.01, 0.10]$).
  3. `execute_tools`: Bounded invocation of approved business tools with active DB session and per-tool error recovery.
  4. `synthesize_response`: Evidence-grounded synthesis linking numerical metrics (`[METRIC:...]`) and document citations (`[DOC-N: ...]`).

### 2. Approved Business Analysis Tools (7 Approved Tools)
1. `get_business_kpis`: Invokes deterministic Pandas analytics for net revenue, order volume, AOV, and cancellation rates.
2. `analyze_revenue_trends`: Computes monthly aggregated revenue timeline with period-over-period growth rates.
3. `get_product_performance`: Ranks catalog items by total revenue and unit volumes sold.
4. `forecast_sales`: Runs XGBoost recursive multi-step forecasting with 95% confidence intervals and holdout WAPE metrics.
5. `detect_anomalies`: Runs Isolation Forest statistical outlier detection with explainable pattern tags.
6. `retrieve_business_documents`: Semantic search over workspace PDF/TXT documents using sentence-transformers.
7. `generate_executive_report`: Executes the full three-stage Jinja2 prompt engineering pipeline.

### 3. Security Guardrails & Tenant Isolation
* **Zero Arbitrary Execution:** No `eval`/`exec`, no raw SQL generation.
* **Workspace Scoping:** Every tool call verifies `workspace_id` membership; demo datasets bypass authentication safely without leaking tenant data.
* **Bounded Invocations:** Enforced maximum of 7 tools per turn with timeout bounds.
* **Prompt Injection Defense:** Regex sanitizer catches adversarial injection attempts and drops to security alert before tool dispatch.
* **Unsupported Query Safe Fallback:** Non-commercial domain queries safely redirected with commercial BI scope explanation.

### 4. Professional AI Copilot UI
* Created [frontend/src/pages/AICopilotPage.tsx](file:///d:/Insightforge/frontend/src/pages/AICopilotPage.tsx).
* Features:
  - Chat interface with user/assistant message bubbles, timestamps, and demo mode indicator.
  - Quick-start prompt chips for KPIs, Trends, Forecast, Anomalies, Products, and Executive Reports.
  - Collapsible **Execution Trace Drawer** detailing executed tools, parameters, latency in milliseconds, and status chips.
  - Interactive **Recharts Visualizations** (KPI scorecards, revenue area charts, horizontal product bars, forecast with 95% CI bands, and anomaly distribution histograms).
  - Clickable **Evidence References** (`[METRIC:...]` and `[DOC-N: ...]`).
  - Session management with persistent history and "New Chat" button.
* Navigation: Registered in `App.tsx` (`/copilot`, `/ai-copilot`), [Sidebar.tsx](file:///d:/Insightforge/frontend/src/components/layout/Sidebar.tsx) (with "Stage 8" badge), and [BottomNav.tsx](file:///d:/Insightforge/frontend/src/components/layout/BottomNav.tsx).

### 5. Automated Verification & Test Suite
* **Backend Pytest:** **101 Passed, 0 Failed** across all test suites (including 13 dedicated agent tests in `test_agent.py`).
* **Frontend Vitest:** **10 Passed, 0 Failed**.
* **Frontend Production Build:** Clean build via `npm run build` (2,133 modules transformed into `dist/` in 7.24s).
