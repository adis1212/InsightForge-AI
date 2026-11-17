# InsightForge AI

> **Mobile-First B2B SaaS Augmented Analytics Platform**  
> *Third-Year Computer Science Prompt Engineering Capstone Project*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

InsightForge AI is an augmented analytics B2B SaaS platform engineered for wholesale distributors and multi-channel merchants. It integrates deterministic tabular data intelligence with structured, evidence-grounded AI reasoning.

### The InsightForge Principle:
> **Never ask an LLM to perform mathematical calculations.**  
> InsightForge AI calculates 100% of numerical KPIs using vectorized Pandas engines. Generative AI systems receive verified numerical artifacts as immutable evidence bounds, eliminating arithmetic hallucination while maximizing strategic decision utility.

---

## 🚀 Key Features

### 1. Evidence-Grounded Prompt Engineering Engine (Stage 5 — Prompt 2)
* **3-Stage Chained Prompt Pipeline:**
  - **Stage 1 (Factual Summarization):** Verified Pandas KPI JSON $\rightarrow$ Grounded factual statements with structured `[METRIC:metric_id]` citations.
  - **Stage 2 (Strategic Insights):** Validated factual claims $\rightarrow$ Explicit hypotheses labeled `[HYPOTHESIS]`, operational risks, and metric-tied recommendations.
  - **Stage 3 (Executive Report):** Validated findings $\rightarrow$ Strict JSON adhering to the Pydantic `ExecutiveCommercialReport` schema.
* **Mandatory Refusal Constraint:** Enforces `"Insufficient data"` for unsupported causal factors and profit margins when item cost records (COGS) are missing.
* **Prompt Versioning (v1 vs. v2):** Stored Jinja2 templates comparing baseline unconstrained prompts against evidence-grounded structured architectures.
* **Deterministic Verification Engine:** Automated numerical verification against metric IDs (0.5% tolerance), schema auditing, and markdown cleanup.
* **Automated Evaluation Harness:** `backend/scripts/evaluate_prompts.py` evaluates v1 vs. v2 across 4 golden benchmark datasets (+66.7% accuracy improvement, 100% schema pass rate).
* **Interactive Prompt Studio UI:** Live chain execution, side-by-side A/B comparison, evaluation scorecard viewer, and Jinja2 template diffs.

### 2. Machine Learning Intelligence (Stage 6)
* **Model 1: XGBoost Sales Forecasting Engine:**
  - Time-series aggregation with forward-shifted lag (1..4) and rolling features (3/6 periods) preventing target leakage.
  - Chronological 20% holdout validation (no future leakage).
  - Benchmark comparison against a Seasonal Naive lag-1 persistence model using MAE, RMSE, and WAPE.
  - Multi-step recursive forecasting with 95% residual confidence intervals.
* **Model 2: Isolation Forest Transaction Anomaly Detector:**
  - Feature engineering on SKU-relative price/volume deviations, cancellation flags, and off-hour transaction indicators.
  - Normalized continuous anomaly scoring $[0, 1]$ with explainable rule tags (`EXTREME_UNIT_PRICE`, `UNUSUAL_BULK_QUANTITY`, `CANCELLATION_SPIKE`, `OFF_HOURS_ACTIVITY`).
  - Empirical synthetic anomaly injection validation (100% recall on injected outliers).
  - Legal and commercial disclosures distinguishing mathematical outliers from confirmed fraud.
* **Interactive ML Intelligence UI:**
  - Recharts Area/Line visualization with historical actuals, forecast curves, 95% confidence intervals, and naive baseline lines.
  - Anomaly distribution histogram, risk severity breakdown, and searchable flagged transaction table.

### 3. Business Document Knowledge Base & Hybrid RAG Retrieval (Stage 7 — Prompt 4)
* **Multi-Format Ingestion:** PDF (page-by-page text extraction via `pypdf`) and plain-text (`.txt`) documents up to 25 MB.
* **Sliding-Window Chunking:** Word-level sliding window (400 words, 60-word overlap) preserving document title, page number, and chunk provenance.
* **Dense Vector Embeddings:** Embedded using `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dimensional dense vectors).
* **Cosine Similarity Retrieval:** In-memory vector similarity with 0.25 minimum similarity threshold floor (~12.8 ms warm latency).
* **Prompt Injection Sanitization:** Neutralizes malicious directives (`IGNORE PREVIOUS INSTRUCTIONS`, etc.) at ingestion time.
* **Multi-Tenant Scoping:** Strict workspace-level isolation on all queries preventing cross-tenant data leaks.
* **AI Prompt Grounding:** Grounded document citations (`[DOC-N] Title (Source)`) injected into Prompt Stage 2 without mathematical contamination.
* **Interactive Knowledge Base UI:**
  - Drag-and-drop document uploader with progress indicators.
  - Indexed documents table with passage count, file size, and deletion controls.
  - Semantic search explorer with similarity score meters and citation summaries.
  - RAG design rules, security disclosures, and architectural specifications tab.

### 4. Controlled Agentic AI Business Analyst (Stage 8 — Prompt 5)
* **Controlled LangGraph State Machine:** 4-node deterministic graph (`classify_and_plan` $\rightarrow$ `validate_arguments` $\rightarrow$ `execute_tools` $\rightarrow$ `synthesize_response`).
* **7 Approved Business Tools:**
  1. `get_business_kpis`: Pandas deterministic commercial metrics.
  2. `analyze_revenue_trends`: Monthly revenue timeline with growth rates.
  3. `get_product_performance`: Top products by revenue and unit volumes.
  4. `forecast_sales`: XGBoost time-series forecast with confidence intervals.
  5. `detect_anomalies`: Isolation Forest statistical outlier detection.
  6. `retrieve_business_documents`: Semantic search over indexed documents with cosine similarity.
  7. `generate_executive_report`: Three-stage Jinja2 prompt engineering chain.
* **Security & Bounded Execution:**
  - Zero arbitrary code execution (`eval`/`exec` strictly forbidden) and zero raw SQL generation.
  - Bounded tool execution limits (max 7 tools/turn, bounded forecast horizons and product limits).
  - Multi-tenant workspace scoping verified on every invocation.
  - Prompt injection defense and immediate refusal for adversarial instructions.
  - Unsupported query fallback for non-commercial domains.
* **Interactive AI Copilot UI:**
  - Conversational chat interface with demo mode badge and message history.
  - Quick-start prompt chips for KPIs, Trends, Forecast, Anomalies, Products, and Boardroom Reports.
  - Collapsible **Execution Trace Drawer** detailing executed tools, parameters, latency in milliseconds, and status chips.
  - Inline **Recharts Visualizations** (KPI scorecards, revenue area curves, product rankings, forecast with 95% CI bands, and anomaly distribution histograms).
  - Clickable **Evidence Citations** linking metrics and document references.

### 5. Deterministic Analytics Engine (Stages 1–3)
* Gross and net revenue aggregations (excluding cancellations prefixed with `'C'`).
* Unique order volume, units sold, and Average Order Value (AOV).
* Unique customer tracking (excluding null identifiers).
* Cancellation & return rate computation with revenue reversal impact.
* Month-over-month revenue growth trajectories with zero-division protection.
* Product performance leaderboards and international geographic rankings.

### 3. Full-Stack SaaS Foundation (Stage 2 & 4)
* **Multi-Tenant Workspaces:** Scoped data isolation, salted `bcrypt` password hashing, and HMAC-SHA256 JWT tokens.
* **File Ingestion:** CSV and Excel (`.xlsx`, `.xls`) parsing with automatic column role detection and data quality audits.
* **Mobile-First PWA:** Navy/Slate/Teal palette, persistent light/dark theme switch, bottom navigation on mobile (< 768px), and desktop sidebar ($\ge$ 768px).

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI, Pydantic v2
- **Agent Workflows:** LangGraph (StateGraph), LangChain Core
- **Prompt Engineering & RAG:** Jinja2 templates, VerificationEngine, sentence-transformers (`all-MiniLM-L6-v2`), pypdf, Provider Abstraction (Local Demo, OpenAI, Gemini)
- **Machine Learning:** XGBoost Regressor, scikit-learn IsolationForest, Joblib
- **Database & ORM:** SQLAlchemy 2.0 (PostgreSQL + SQLite support), Alembic
- **Analytics:** Pandas 2.2, NumPy 2.2, openpyxl
- **Security:** bcrypt, python-jose (JWT)
- **Testing & Quality:** Pytest (101 tests), Ruff

### Frontend
- **Framework:** React 18, TypeScript, Vite
- **Styling:** Tailwind CSS, Radix UI primitives, Lucide React
### 4. Controlled Agentic AI Business Analyst (Stage 8 — Prompt 5)
* **LangGraph Stateful Agent Architecture:**
  - 4-node deterministic topology (`classify_and_plan`, `validate_arguments`, `execute_tools`, `synthesize_response`).
  - 7 approved business tools (`get_business_kpis`, `analyze_revenue_trends`, `get_product_performance`, `forecast_sales`, `detect_anomalies`, `retrieve_business_documents`, `generate_executive_report`).
* **Security & Boundary Controls:**
  - Zero arbitrary code execution (`eval`/`exec`) and zero raw SQL generation.
  - Multi-tenant workspace validation, parameter boundary clamping, and adversarial prompt injection defense.
* **AI Copilot UI:** Interactive chat, execution trace drawer (tool parameters, status, latency), and interactive Recharts visualizations.

### 5. Boardroom Executive PDF Reports & Progressive Web App (Stage 9 — Prompt 6)
* **Vector-Rendered Multi-Page PDF Engine:**
  - Built with ReportLab using custom `NumberedCanvas` (`Page X of Y`), running headers, and corporate styling.
  - 3 embedded high-resolution Matplotlib figures: Monthly Revenue Area, XGBoost Forecast with 95% Confidence Intervals vs Baseline, and Isolation Forest Anomaly Histogram.
  - 8 structured audit sections: Executive Brief, Verified KPI Scorecard, Revenue Trends, ML Predictive Intelligence, Knowledge Citations, Prioritized Strategic Recommendations, Assumptions & Limitations, Verification Metadata.
  - 100% deterministic arithmetic grounding: zero LLM calculation hallucination.
* **Report History & REST API:** Complete persistence via `ReportRecord` model; endpoints for generation, listing, JSON inspection, binary download, and deletion.
* **Progressive Web App (PWA):** Web App Manifest and Service Worker with offline bundle caching and strict network-only bypass for `/api/`.
* **Full-Spectrum Academic Evaluation (12 Benchmarks):** Automated benchmark harness (`backend/scripts/run_academic_evaluation.py`) verifying Prompt v1 vs v2, XGBoost vs Seasonal Naive, Isolation Forest outlier recall, RAG latency, and agent routing accuracy.

- **Visualization:** Recharts
- **Testing:** Vitest (10 tests), ESLint 9

---

## 🏃 Quick Start (Local Development)

### 1. Run Backend Server
```powershell
Set-Location d:\Insightforge\backend

# Run automated tests (110 tests)
python -m pytest app/tests/ -v

# Run full academic research evaluation suite (12 benchmarks)
python scripts/run_academic_evaluation.py

# Start development API server
uvicorn app.main:app --reload --port 8000
```
Interactive API Documentation will be live at: `http://localhost:8000/api/docs`

### 2. Run Frontend Client
```powershell
Set-Location d:\Insightforge\frontend

# Run unit tests (10 tests)
npm test

# Build production bundle
npm run build

# Start Vite development server
npm run dev
```
Application interface will be live at: `http://localhost:5173`  
Navigate to `/reports` for Executive PDF Reports or `/copilot` for the AI Business Analyst!

---

## 📚 Academic Capstone Deliverables
- [FINAL_PROJECT_REPORT_OUTLINE.md](file:///d:/Insightforge/FINAL_PROJECT_REPORT_OUTLINE.md) — Comprehensive Capstone Research Outline
- [DEMO_SCRIPT.md](file:///d:/Insightforge/DEMO_SCRIPT.md) — Step-by-Step Viva Presentation & Demo Script
- [VIVA_QUESTIONS.md](file:///d:/Insightforge/VIVA_QUESTIONS.md) — Rigorous Defense Q&A for Academic Examiners
- [DEPLOYMENT_GUIDE.md](file:///d:/Insightforge/DEPLOYMENT_GUIDE.md) — Production Deployment & Docker Containerization Guide
- [EVALUATION.md](file:///d:/Insightforge/EVALUATION.md) — Complete 12-Benchmark Academic Evaluation Methodology
- [DECISIONS.md](file:///d:/Insightforge/DECISIONS.md) — Architectural Decision Records (ADR-001 through ADR-014)


---

## 📄 License

MIT License. Developed for academic research in Prompt Engineering and AI-Augmented Analytics.
