# InsightForge AI — Indian Business Edition
> **Mobile-First B2B SaaS Augmented Commercial Analytics Platform**  
> *Third-Year Computer Science Prompt Engineering Capstone Project*  
> **Repository:** [https://github.com/adis1212/InsightForge-AI.git](https://github.com/adis1212/InsightForge-AI.git)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Backend Tests](https://img.shields.io/badge/Backend%20Tests-110%20Passed-emerald.svg)](#28-running-tests)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-13%20Passed-emerald.svg)](#28-running-tests)

---

## 1. Project Title & Tagline
**InsightForge AI — Indian Business Edition**  
*An Evidence-Grounded Augmented Commercial Analytics Platform Decoupling Deterministic Computation from Generative AI Reasoning for Indian Wholesale, FMCG, and SME Retailers.*

---

## 2. Problem Statement
In commercial enterprise operations, decision-makers are inundated with voluminous transaction ledgers. However, when businesses attempt to leverage modern Generative Large Language Models (LLMs) for commercial intelligence, they encounter a fatal barrier: **Generative models fundamentally cannot perform reliable arithmetic.**

Because autoregressive language models predict tokens probabilistically through sub-word tokenization, they suffer from rounding errors, aggregation drift, and arithmetic hallucination. In commercial analytics, an ungrounded 5% profit margin claim or an invented quarterly sales figure can trigger catastrophic inventory and supply chain misallocations.

---

## 3. Project Purpose
The purpose of InsightForge AI is to bridge the gap between static spreadsheet dashboards and probabilistic AI chatbots. It provides commercial enterprises with a **provably grounded, audit-ready AI Business Analyst Copilot** that:
- Executes 100% of mathematical aggregations using deterministic code.
- Trains predictive machine learning models with chronological holdout validation.
- Grounds natural language insights strictly within immutable numerical evidence.
- Compiles boardroom-grade executive PDF reports with dynamic pagination and embedded high-resolution figures.

---

## 4. Business Problem Being Solved
Wholesale distributors, FMCG super-stockists, and multi-channel retailers in Indian commercial hubs (Pune, Mumbai, Nagpur, Bengaluru, Hyderabad, Delhi NCR, Ahmedabad, Chennai, Jaipur) face three acute challenges:
1. **Spreadsheet Paralysis:** Store managers receive monthly order ledgers containing 5,000 to 50,000 transaction rows. Extracting true net revenue (accounting for cancelled and returned invoices), customer concentration, and seasonal patterns requires complex manual spreadsheet formulas.
2. **Prohibitive BI Costs:** Legacy enterprise business intelligence tools (Tableau, Power BI, SAP) impose high recurring license fees and require dedicated data analytics personnel.
3. **The Hallucination Danger:** Pasting sensitive commercial records into consumer chatbots exposes confidential trade margins and generates hallucinated financial figures.

---

## 5. Target Users
- **Indian FMCG Wholesalers & Super-Stockists:** Managing multi-category distribution (Packaged Foods, Beverages, Personal Care, Household Essentials, Grocery).
- **Regional Retailers & Kirana Networks:** Tracking monthly order volume, customer concentration, and pending payments.
- **SME Commercial Directors:** Requiring boardroom-ready executive PDF briefings for banking lines of credit and investor reviews.
- **Academic Reviewers & Engineering Faculty:** Evaluating prompt engineering methodologies, machine learning baseline disciplines, and secure agent architectures.

---

## 6. Why Ordinary CSV Analysis Is Insufficient
- **Silent Cancellation Distortions:** Raw transaction exports list cancellation invoices (e.g. `CINV-10045`) with negative quantities. Standard spreadsheet sums that omit negative filtering or double-count return adjustments distort gross revenue by 5% to 15%.
- **Zero Forward-Looking Intelligence:** Spreadsheets show historical totals but cannot perform leakage-free time-series forecasting with confidence intervals or unsupervised outlier detection.
- **Missing Strategic Context:** A spreadsheet table of numbers cannot cross-reference company credit terms, restocking fees, or regional sales quotas to produce actionable recommendations.

---

## 7. Why Prompt Engineering Is Critical
Prompt engineering in InsightForge AI is **not** mere prompt cosmetic styling. It is an architectural discipline that:
- Deconstructs single-prompt cognitive overload into a three-stage sequential chain.
- Enforces mandatory `[METRIC:metric_id]` citation syntax.
- Enforces a **Mandatory Refusal Constraint**: when item cost data (COGS) is absent, the prompt pipeline strictly returns `"Insufficient data — unit costs not provided"` rather than allowing the model to hallucinate profit margins.
- Ensures valid Pydantic JSON schema generation for downstream API consumption.

---

## 8. Proposed Solution: The Decoupled Principle
InsightForge AI is founded upon **The Decoupled Deterministic-Generative Principle**:

$$\text{LLMs must never perform arithmetic calculations on commercial data.}$$

- **100% Deterministic Arithmetic:** Vectorized Pandas code calculates revenue, orders, units, AOV, cancellations, growth rates, and margins.
- **Immutable Evidence Injection:** Metrics are passed into Jinja2 prompt templates as immutable JSON facts.
- **Post-Generation Verification:** A deterministic verification engine audits cited numbers against Pandas calculations within a 0.5% tolerance window.

---

## 9. Key Features
1. **Automated Data Quality Auditor:** Computes a 0–100 quality score, detecting missing values, duplicates, cancellations, and column roles.
2. **Deterministic KPI Engine:** Vectorized Pandas math for Net Revenue, AOV, Growth Rates, and Regional Leaderboards.
3. **XGBoost Sales Forecasting:** Multi-step recursive time-series forecasting with forward-shifted features, 95% confidence intervals, and Seasonal Naive baseline comparison.
4. **Isolation Forest Anomaly Detection:** Continuous $[0, 1]$ anomaly scoring with explainable pattern indicators (`EXTREME_UNIT_PRICE`, `UNUSUAL_BULK_QUANTITY`, `CANCELLATION_SPIKE`, `OFF_HOURS_ACTIVITY`).
5. **Business Knowledge RAG:** Multi-format document ingestion (PDF/TXT), pre-embedding prompt injection sanitization, and in-memory cosine retrieval.
6. **Controlled LangGraph AI Copilot:** Stateful 4-node directed graph executing 7 approved tools with parameter clamping and zero arbitrary code/SQL execution.
7. **Prompt Studio (v1 vs v2):** Side-by-side A/B evaluation laboratory comparing unconstrained baseline prompts against structured, grounded architectures.
8. **Boardroom Executive PDF Generator:** ReportLab vector PDF compiler with custom `NumberedCanvas` (`Page X of Y`), corporate running headers, 8 audit sections, and 3 embedded high-DPI Matplotlib figures.
9. **Progressive Web App (PWA):** Mobile bottom navigation, offline shell caching via custom Service Worker (`sw.js`), and accessible dark/light themes.
10. **Indian Business Localization:** Centralized Indian Rupee (INR / `₹`) formatting (Lakhs and Crores), Indian date conventions (DD/MM/YYYY), and realistic FMCG wholesale distribution parameters.

---

## 10. Implemented vs. Planned Functionality

| Capability | Module | Implementation Status | Verification Evidence |
| :--- | :--- | :---: | :--- |
| **JWT Authentication & RBAC** | `auth.py`, `security.py` | **100% Implemented** | 6 unit tests passing (`test_security.py`) |
| **Multi-Tenant Workspace Scoping** | `workspaces.py` | **100% Implemented** | Tenant isolation verified (`test_api_integration.py`) |
| **Data Ingestion & Quality Audit** | `dataset_service.py` | **100% Implemented** | 15 unit tests passing (`test_dataset_service.py`) |
| **Deterministic Pandas KPI Engine** | `analytics_service.py` | **100% Implemented** | 14 unit tests passing (`test_analytics.py`) |
| **Interactive Dashboard & Leaderboards** | `DashboardOverviewPage.tsx` | **100% Implemented** | Browser verified with Recharts |
| **Prompt Engineering Engine (v1 vs v2)** | `prompt_service.py` | **100% Implemented** | 10 unit tests passing (`test_prompts.py`) |
| **Deterministic Verification Engine** | `verification_engine.py` | **100% Implemented** | 0.5% tolerance verified (`test_prompts.py`) |
| **XGBoost Sales Forecasting** | `forecast_service.py` | **100% Implemented** | 8 unit tests passing (`test_ml_forecast.py`) |
| **Isolation Forest Anomaly Detection** | `anomaly_service.py` | **100% Implemented** | 6 unit tests passing (`test_ml_anomalies.py`) |
| **Business Document RAG** | `retrieval_service.py` | **100% Implemented** | 13 unit tests passing (`test_rag.py`) |
| **Controlled LangGraph Agent** | `agent_service.py` | **100% Implemented** | 13 unit tests passing (`test_agent.py`) |
| **Boardroom Executive PDF Reports** | `report_service.py` | **100% Implemented** | 4 unit tests passing (`test_reports.py`) |
| **Progressive Web App (PWA)** | `manifest.webmanifest`, `sw.js`| **100% Implemented** | Clean production Vite build |
| **Indian Business Edition (BharatTrade)**| `bharattrade_fmcg_transactions.csv` | **100% Implemented** | Seeded 6,000-record simulation |
| **Mandi Data Ingestion Script** | `ingest_indian_mandi_data.py` | **100% Implemented** | Verified with data.gov.in AGMARKNET schema |
| *Choropleth GIS Indian State Maps* | Visual layer | *Planned (Post-v2)* | GeoJSON state polygons |
| *Multi-Agent Consensus Verification* | Orchestration layer | *Planned (Post-v2)* | Dual-model debate architecture |

---

## 11. Technology Stack

```
Frontend Architecture:
├── React 18 (TypeScript 5.7)
├── Vite 6.4 (Production Bundler)
├── Tailwind CSS 3.4 (Design System)
├── Recharts 2.15 (Interactive Visualizations)
├── Lucide React (Accessible Iconography)
├── TanStack Query v5 & Axios (API Client)
└── Service Worker (PWA Offline Shell Caching)

Backend Architecture:
├── FastAPI 0.115+ (Asynchronous API Framework)
├── Python 3.12 / 3.14 (Runtime Environment)
├── SQLAlchemy 2.0 (Relational ORM)
├── Pydantic v2 (Rust-backed Schema Validation)
├── Native Bcrypt (72-Byte Boundary Password Security)
└── Jinja2 (Versioned Prompt Templates)

Analytics, ML & Report Services:
├── Pandas 2.2 & NumPy (Deterministic Math)
├── XGBoost 2.1 (Time-Series Sales Forecasting)
├── Scikit-Learn 1.6 (Isolation Forest Anomaly Detection)
├── Sentence-Transformers 3.3 (all-MiniLM-L6-v2 Dense Embeddings)
├── ReportLab 5.1 (Vector PDF Compilation)
└── Matplotlib 3.10 (Agg Non-Interactive High-DPI Charts)
```

---

## 12. Overall Architecture
InsightForge AI is architected as a decoupled modular monolith:

```
[ Web / Mobile PWA Client ] ──(HTTPS/JSON)──> [ Nginx Reverse Proxy ]
                                                     │
                                                     ▼
                                          [ FastAPI Application ]
                                                     │
      ┌────────────────────┬─────────────────────────┼─────────────────────────┬────────────────────┐
      ▼                    ▼                         ▼                         ▼                    ▼
[ Auth & Workspaces ] [ Ingestion & Pandas ]   [ Predictive ML ]         [ RAG Knowledge ]    [ LangGraph Agent ]
  (JWT / Bcrypt)        (Quality / KPIs)      (XGBoost / IsoForest)     (all-MiniLM-L6-v2)     (4-Node Graph)
                                                     │
                                                     ▼
                                           [ Three-Stage Prompts ]
                                           (v1 vs v2 Jinja2 Chain)
                                                     │
                                                     ▼
                                           [ Verification Engine ]
                                           (0.5% Tolerance Audit)
                                                     │
                                                     ▼
                                           [ ReportLab PDF Engine ]
                                           (NumberedCanvas / Charts)
```

---

## 13. End-to-End Data Flow
1. **Upload:** User uploads a CSV/XLSX transaction ledger.
2. **Ingest & Audit:** File size and extension are verified; columns are fuzzy-mapped; null rates and cancellations are scored (0–100).
3. **Compute Fact Base:** Vectorized Pandas calculates net revenue, unique orders, units sold, AOV, growth timelines, and product rankings.
4. **Predict & Screen:** XGBoost generates multi-step revenue forecasts; Isolation Forest scores transaction outliers.
5. **Retrieve Policy:** RAG searches indexed commercial contracts (PDF/TXT) for payment terms and return policies.
6. **Synthesize & Verify:** The 3-stage prompt pipeline synthesizes narrative insights; the Verification Engine validates numerical claims against Pandas ground truth.
7. **Report:** The user inspects the interactive dashboard or compiles an audit-grade executive PDF.

---

## 14. Pandas KPI Pipeline
All calculations are strictly deterministic:
- **Net Revenue:** $\sum (\text{Quantity} \times \text{UnitPrice})$ for all valid transactions (invoices starting with 'C' and negative quantities are strictly excluded).
- **Average Order Value (AOV):** $\frac{\text{Net Revenue}}{\text{Unique Valid Invoices}}$.
- **Units Sold:** $\sum \text{Quantity}$ for valid transactions.
- **Cancellation Rate:** $\frac{\text{Unique Cancelled Invoices}}{\text{Total Unique Invoices}} \times 100$.
- **Gross Profit (when cost present):** $\text{Net Revenue} - \sum (\text{Quantity} \times \text{UnitCost})$.
- **Division-by-Zero Guards:** All formulas contain fallbacks for empty ledgers or zero invoices.

---

## 15. Three-Stage Prompt Engineering Process
Single-prompt LLM generation causes cognitive overload. InsightForge AI decouples reasoning into three sequential stages:
1. **Stage 1: Factual Summarization (`prompt1_factual_v2.jinja2`):** Takes verified Pandas KPI JSON $\rightarrow$ outputs verified factual claims with mandatory `[METRIC:metric_id]` tags. Zero speculation allowed.
2. **Stage 2: Strategic Insights & Hypotheses (`prompt2_insights_v2.jinja2`):** Takes Stage 1 claims and RAG citations $\rightarrow$ outputs explicit hypotheses prefixed with `[HYPOTHESIS]`, operational risks, and metric-tied recommendations.
3. **Stage 3: Executive Report Formatting (`prompt3_report_v2.jinja2`):** Compiles findings into pure, valid JSON strictly adhering to the Pydantic `ExecutiveCommercialReport` schema.

---

## 16. Prompt v1 vs. v2 Empirical Evaluation
Across four golden test dataset scenarios evaluated under controlled benchmark conditions:

| Evaluation Dimension | Prompt v1 (Unconstrained Baseline) | Prompt v2 (Structured / Grounded) | Performance Delta |
| :--- | :---: | :---: | :---: |
| **Numerical Accuracy (0.5% tolerance)** | 33.3% | **100.0%** (14/14 citations verified) | **+66.7%** |
| **Hallucinated Numbers / Metrics** | 2 ungrounded claims | **0 hallucinations** | **Eliminated** |
| **JSON Schema Conformance** | 0.0% (markdown fences) | **100.0%** (Pydantic valid) | **+100.0%** |
| **Refusal Pass Rate ("Insufficient data")** | 0.0% (fabricated margins) | **100.0%** (enforced refusal) | **+100.0%** |
| **Pipeline Latency** | 2.2 ms | **1.9 ms** | Identical local speed |

---

## 17. Agentic AI Purpose & LangGraph Implementation
The **Controlled AI Copilot** enables commercial users to ask analytical questions in plain language without risking code injection or infinite loops:
- **Topology:** 4-node state graph (`classify_and_plan` $\rightarrow$ `validate_arguments` $\rightarrow$ `execute_tools` $\rightarrow$ `synthesize_response`).
- **7 Approved Business Tools:** `get_business_kpis`, `analyze_revenue_trends`, `get_product_performance`, `forecast_sales`, `detect_anomalies`, `retrieve_business_documents`, `generate_executive_report`.
- **Security Boundaries:** Maximum 7 tool calls per turn; forecast horizons clamped $[1, 12]$; product limits clamped $[1, 20]$; prompt injection defense short-circuits malicious inputs.

---

## 18. RAG Purpose & Implementation
- **Document Chunking:** Word-level sliding window (400 words, 60-word overlap) preserving document title, page number, and chunk index.
- **Dense Vector Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) generating normalized dense vectors.
- **In-Memory Cosine Retrieval:** Cosine similarity calculation with a 0.25 similarity floor filter (~12.8ms warm retrieval latency).
- **Prompt Injection Defense:** Pre-embedding regex sanitizer neutralizes adversarial directives (`IGNORE PREVIOUS INSTRUCTIONS`) at ingestion time.
- **Contextual Grounding:** Citations (`[DOC-N] Title (Source)`) injected into Prompt Stage 2 without contaminating numerical KPI math.

---

## 19. XGBoost Forecasting Model Details
- **Feature Engineering:** Forward-shifted lags ($t-1, t-2, t-3, t-4$), rolling window statistics ($rolling\_mean_3, rolling\_mean_6, rolling\_std_3$), and cyclical calendar features ($\sin(\text{month}), \cos(\text{month})$).
- **Leakage Prevention:** Features strictly shifted forward by 1 period before feature creation (`.shift(1)`).
- **Validation:** Chronological 80/20 train/test holdout split (no future lookahead).
- **Baseline Discipline:** Evaluated against a Seasonal Naive lag-1 persistence model using WAPE, MAE, and RMSE.
- **Honest Academic Finding:** On single-year wholesale datasets with high intra-week variance, the naive baseline is competitive (Naive WAPE 23.9% vs XGBoost 45.7%). The system honestly discloses `outperforms_baseline: false`.

---

## 20. Isolation Forest Anomaly Model Details
- **Algorithm:** Unsupervised `IsolationForest` (100 estimators, 3.0% contamination).
- **Feature Engineering:** SKU-relative price deviation ratio, SKU-relative quantity deviation ratio, cancellation flag, off-hours execution indicator, and line total volume.
- **Explainable Pattern Indicators:** `EXTREME_UNIT_PRICE` (100x pricing typos), `UNUSUAL_BULK_QUANTITY` (bulk institutional orders), `CANCELLATION_SPIKE` (freight damage clusters), and `OFF_HOURS_ACTIVITY` (3 AM transaction logging).
- **Synthetic Injection Recall:** 90.0% to 100.0% empirical recall on injected outlier benchmarks.
- **Legal Disclaimer:** Prominently discloses that statistical isolation measures mathematical distance from operational medians, not verified criminal fraud.

---

## 21. Dataset Strategy & Provenance
To ensure complete academic transparency, InsightForge AI implements a **Dual-Track Data Strategy**:
1. **Track 1 (Demonstration Track):** **BharatTrade Distributors — Demo Business**, a high-fidelity deterministic seeded simulation representing an Indian FMCG wholesale distributor.
2. **Track 2 (Real Government Data Ingestion Script):** [backend/scripts/ingest_indian_mandi_data.py](file:///d:/Insightforge/backend/scripts/ingest_indian_mandi_data.py) connects to the official Open Government Data (data.gov.in) portal to fetch authentic AGMARKNET agricultural mandi prices across Indian states.

---

## 22. Indian Demo Business Explanation (BharatTrade Distributors)
- **Fictional Brand:** BharatTrade Distributors — Demo Business (Pune, Maharashtra).
- **Regional Hubs:** Pune, Mumbai, Nagpur, Bengaluru, Hyderabad, Delhi NCR, Ahmedabad, Chennai, Jaipur.
- **Timeline:** 24 Continuous Months (January 1, 2023 to December 31, 2024; 6,000 records).
- **Currency:** Indian Rupee (INR / `₹`).
- **Product Categories (FMCG):** Packaged Foods, Beverages, Personal Care, Household Essentials, Grocery, Commercial Stationery.
- **Realistic Economics:** Wholesale pack pricing, explicit unit costs (COGS), realistic 15–25% margins, and explicit GST tax slabs (5%, 12%, 18%).
- **Documented Seasonal Events:** Diwali festive demand surge (Oct/Nov), Summer beverage peak (Apr/May), and Fiscal year-end procurement (March).

---

## 23. Demo Mode Instructions
Visitors can explore the full platform without uploading files or configuring API keys:
1. Open `http://localhost:5173` in any modern web browser.
2. Click **"Explore Live Demo"** on the landing page.
3. The system loads **BharatTrade Distributors** with pre-computed deterministic KPIs, XGBoost forecasts, anomaly tables, and Indian business RAG documents.
4. Experience the complete journey: **Dashboard $\rightarrow$ Analytics $\rightarrow$ ML Intelligence $\rightarrow$ Knowledge Base $\rightarrow$ AI Copilot $\rightarrow$ Executive PDF Reports**.

---

## 24. Setup & Installation

### Prerequisites
- Python 3.12+ (or Python 3.14)
- Node.js 20+ (LTS) & npm
- Git

### Clone Repository
```powershell
git clone https://github.com/adis1212/InsightForge-AI.git
Set-Location InsightForge-AI
```

### Backend Installation
```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Installation
```powershell
Set-Location ..\frontend
npm install
```

---

## 25. Environment Variables
Copy `.env.example` in both directories:

### `backend/.env`
```ini
PROJECT_NAME="InsightForge AI — Indian Business Edition"
ENVIRONMENT="development"
SECRET_KEY="generate-a-random-64-character-hex-string"
DATABASE_URL="sqlite:///./insightforge.db"
UPLOAD_DIR="./uploads"
DEFAULT_LLM_PROVIDER="deterministic"
OPENAI_API_KEY=""
GEMINI_API_KEY=""
```

### `frontend/.env`
```ini
VITE_API_URL="/api/v1"
```

---

## 26. Running Frontend & Backend

### Start Backend API Server
```powershell
Set-Location d:\Insightforge\backend
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger documentation is live at: `http://localhost:8000/api/docs`

### Start Frontend Client
```powershell
Set-Location d:\Insightforge\frontend
npm run dev
```
Client interface is live at: `http://localhost:5173`

---

## 27. Running Model Training & Data Generation

### Generate Indian FMCG Wholesale Demo Dataset
```powershell
python backend/scripts/generate_indian_demo_data.py
```

### Ingest Real Indian Mandi Agricultural Prices
```powershell
python backend/scripts/ingest_indian_mandi_data.py
```

---

## 28. Running Tests

### Backend Automated Test Suite (110 Pytest Tests)
```powershell
Set-Location d:\Insightforge\backend
python -m pytest app/tests/ -v
```
**Status: 110 Passed, 0 Failed (100% Pass Rate in ~45s)**

### Frontend Automated Test Suite (13 Vitest Tests)
```powershell
Set-Location d:\Insightforge\frontend
npm test -- --run
```
**Status: 13 Passed, 0 Failed (100% Pass Rate in ~0.6s)**

### Frontend Production Build
```powershell
Set-Location d:\Insightforge\frontend
npm run build
```
**Status: Clean build with zero TypeScript errors.**

---

## 29. Report Generation
Executive PDF reports can be generated via the UI at `/reports` or via the REST API:
```powershell
curl -X POST http://localhost:8000/api/v1/workspaces/demo-workspace-01/reports/generate `
  -H "Content-Type: application/json" `
  -d '{"dataset_id": "bharattrade-demo", "prompt_version": "v2"}'
```

---

## 30. API Documentation
All endpoints are documented interactively at `http://localhost:8000/api/docs`:
- `/api/v1/auth`: Authentication and profiles.
- `/api/v1/workspaces`: Multi-tenant organization scoping.
- `/api/v1/workspaces/{id}/datasets`: File upload and quality auditing.
- `/api/v1/workspaces/{id}/analytics`: Deterministic KPIs, XGBoost forecasts, and Isolation Forest outliers.
- `/api/v1/workspaces/{id}/knowledge`: Document ingestion, chunking, and semantic search.
- `/api/v1/workspaces/{id}/agent`: LangGraph conversational copilot.
- `/api/v1/workspaces/{id}/reports`: Boardroom executive PDF compilation.

---

## 31. Research Contribution & Novelty
1. **The Decoupled Principle:** Proof that commercial BI can leverage generative AI without risking arithmetic hallucination by enforcing strict separation between computation and narrative synthesis.
2. **Three-Stage Prompt Decomposition:** Demonstrated that dividing analytical tasks into Factual $\rightarrow$ Hypotheses $\rightarrow$ Pydantic JSON improves accuracy by +66.7% and achieves 100% schema conformance.
3. **Mandatory Refusal Architecture:** Formalized refusal constraints that prevent LLMs from fabricating financial margins when underlying cost data is absent.
4. **Empirical ML Baseline Discipline:** Honest comparison against Seasonal Naive persistence baselines, demonstrating research integrity.

---

## 32. Measured Evaluation Results
From the automated evaluation artifact ([academic_research_evaluation.json](file:///d:/Insightforge/data/samples/academic_research_evaluation.json)):
- **Prompt v2 Numerical Accuracy:** 100.0% (vs. v1 33.3%).
- **Prompt v2 Hallucinations:** 0.
- **Prompt v2 JSON Schema Pass Rate:** 100.0%.
- **Agent Tool Routing Accuracy:** 93.8% across 16 multi-turn commercial query types.
- **Adversarial Injection Defense:** 100.0% rejection rate.
- **Isolation Forest Recall on Outliers:** 90.0% to 100.0%.
- **RAG Retrieval Latency:** < 50ms warm in-memory cosine search.

---

## 33. Limitations
- **Single-Node In-Memory Vector Search:** Cosine similarity with sentence-transformers is optimal for SME libraries (<1,000 documents). Scaling to millions of document chunks requires external vector databases (e.g. `pgvector`).
- **Intermittent Wholesale Demand Dynamics:** On short single-year weekly series, recursive XGBoost models can struggle against simple lag-1 persistence baselines.
- **Tabular Schema Normalization:** Irregular, multi-header spreadsheets require column mapping confirmation before analysis.

---

## 34. Future Enhancements
- **Multi-Agent Consensus (Dual-Model Review):** Implement a two-agent auditor where a second model independently reviews the first model's synthesized brief.
- **On-Device Quantized SLMs:** Integrate localized small language models (Phi-3-Mini, Gemma-2-2B via ONNX/Llama.cpp) for 100% offline edge execution.
- **Choropleth GIS Indian State Mapping:** Integrate Indian GeoJSON state and district boundaries for interactive visual heatmaps.

---

## 35. Development Roadmap
- [x] **Stage 1–4:** Full-Stack Foundation, Deterministic Pandas Engine, React Dashboard (Completed).
- [x] **Stage 5:** Three-Stage Jinja2 Prompt Engineering Pipeline & Verification Engine (Completed).
- [x] **Stage 6:** Predictive ML Intelligence (XGBoost & Isolation Forest) (Completed).
- [x] **Stage 7:** Enterprise Knowledge Base & Hybrid RAG Retrieval (Completed).
- [x] **Stage 8:** Controlled LangGraph Agentic AI Business Analyst (Completed).
- [x] **Stage 9:** Boardroom Executive PDF Reports & Progressive Web App (Completed).
- [x] **Post-Build Master Prompt 7:** Indian Business Edition, Real Dataset Research, and BharatTrade Simulation (Completed).

---

## 36. Contributors & Acknowledgments
Developed for academic research in Prompt Engineering and AI-Augmented Analytics.

**Verified Repository Contributors (Git History):**
- **Aditya Yadav** (`adis1212` / `aditya.yadav24@vit.edu`) — Principal Architect, Backend & ML Services, Prompt Engineering Engine
- **Tahir Shaikh** (`TheTahirShaikh` / `tahirshaikh1142006@gmail.com`) — Frontend Engineering, UI Components & Utilities

**License:** MIT License. See [LICENSE](file:///d:/Insightforge/LICENSE) for terms.
