# InsightForge AI — Comprehensive Project Audit
**Audit Date:** November 17, 2026  
**Auditor:** Principal AI Product Architect, Senior Data Scientist, QA Lead  
**Scope:** Full-Stack Architecture, Backend APIs, Machine Learning Services, Prompt Engineering, RAG Knowledge Base, Agent Workflows, Frontend Client, Database Models, and Currency/Locale Handling.

---

## 1. Executive Summary

InsightForge AI was architected as a modular monolith B2B SaaS platform for augmented commercial analytics. Across Prompts 1 through 6, core functionality across all 9 stages was built and verified:
- **Backend Test Suite:** 110 passed Pytest tests covering analytics, ML, RAG, agent routing, PDF generation, security, and full lifecycle end-to-end integration.
- **Frontend Test Suite:** 8 passing tests, with 2 tests currently failing due to discrepancies between commit `871be7a` (`utils.ts`) and expected null/sign handling in `utils.test.ts`.
- **Currency & Regional Assumptions:** Currently hardcoded to USD (`$`) in backend formatters (`analytics_service.py`), and the default benchmark dataset (`synthetic_wholesale.csv`) reflects Western industrial parts with shipments to Germany, the UK, and the USA.
- **Indian Market Readiness:** Requires immediate localization for Indian SMB/FMCG distribution, including INR (`₹`) formatting (Lakhs/Crores), realistic Indian geography (Pune, Mumbai, Nagpur, Bengaluru, etc.), Indian product categories, GST distinctions, and a dedicated, isolated Indian demo business (**BharatTrade Distributors**).

---

## 2. Detailed Module-by-Module Audit Matrix

### Module 1: Authentication & User Management
* **Purpose:** Multi-tenant user registration, secure authentication, and profile retrieval.
* **Implementation Location:** `backend/app/api/v1/endpoints/auth.py`, `backend/app/core/security.py`, `backend/app/models/user.py`.
* **Technology Used:** FastAPI, SQLAlchemy 2.0, JWT (HMAC-SHA256), native `bcrypt` (with explicit 72-byte truncation boundary).
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Fully connected via `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`.
* **Test Status:** Verified passing in `test_security.py` and `test_api_integration.py`.
* **Known Limitations:** Password reset and email confirmation workflows are not implemented (by design for local/demo scope).
* **Suggested Improvements:** Add optional OTP or session expiration alerts for mobile users.

---

### Module 2: Multi-Tenant Workspace Scoping
* **Purpose:** Strict tenant isolation, preventing cross-organization commercial data leakage.
* **Implementation Location:** `backend/app/api/v1/endpoints/workspaces.py`, `backend/app/models/workspace.py`.
* **Technology Used:** PostgreSQL/SQLite relational schema with `WorkspaceMember` role-based access control.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Fully connected; `_check_workspace_access` validates every tenant route.
* **Test Status:** Verified passing in `test_api_integration.py` (including 403 Forbidden checks).
* **Known Limitations:** Demo mode workspaces use prefix `demo-` to bypass strict authentication while retaining tenant isolation.
* **Suggested Improvements:** Support default pre-seeded Indian demo business workspace automatically on first launch.

---

### Module 3: Dataset Ingestion & File Upload
* **Purpose:** Multi-format file upload validation (CSV, XLSX, XLS) bounded to 50 MB.
* **Implementation Location:** `backend/app/api/v1/endpoints/datasets.py`, `backend/app/services/dataset_service.py`.
* **Technology Used:** Python `pandas`, `openpyxl`, `xlrd`, FastAPI multipart form handler.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Fully connected via `/api/v1/workspaces/{id}/datasets/upload`.
* **Test Status:** 15 tests passing in `test_dataset_service.py`.
* **Known Limitations:** In-memory DataFrame conversion for large files (>50 MB rejected).
* **Suggested Improvements:** Add chunked streaming parsing if larger Indian mandi price archives are uploaded.

---

### Module 4: Column Auto-Detection & Schema Mapping
* **Purpose:** Automatically detect business roles (`invoice_no`, `stock_code`, `description`, `quantity`, `unit_price`, `customer_id`, `country`/`region`, `date`).
* **Implementation Location:** `backend/app/services/dataset_service.py` (`detect_column_roles`).
* **Technology Used:** Regex fuzzy string matching with normalized header patterns.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `/preview` and `/mapping` override endpoints.
* **Test Status:** Verified passing in `test_dataset_service.py`.
* **Known Limitations:** Currently looks for `country` rather than `state` or `city`.
* **Suggested Improvements:** Add aliases for Indian commercial headers: `state`, `city`, `district`, `mandi`, `cogs`, `product_cost`, `gst_rate`, `tax`.

---

### Module 5: Data Quality Auditor
* **Purpose:** Pre-analytics audit scoring (0–100) identifying missing values, duplicates, invalid dates, and cancellation transactions.
* **Implementation Location:** `backend/app/services/dataset_service.py` (`audit_data_quality`).
* **Technology Used:** Vectorized Pandas null and duplicate checks.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `GET /workspaces/{id}/datasets/{id}/quality`.
* **Test Status:** Verified passing in `test_dataset_service.py`.
* **Known Limitations:** Does not check for currency consistency or mixed currencies.
* **Suggested Improvements:** Add currency detection/validation flag in the quality score card.

---

### Module 6: Deterministic KPI Analytics Engine
* **Purpose:** Execute 100% of mathematical aggregations deterministically (Zero LLM arithmetic).
* **Implementation Location:** `backend/app/services/analytics_service.py`.
* **Technology Used:** Pandas, NumPy.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Fully connected via `GET /workspaces/{id}/analytics/{id}` and `/summary`.
* **Test Status:** 14 tests passing in `test_analytics.py`.
* **Known Limitations:**
  - Formatted strings hardcode USD (`$1,248,950.45`).
  - Unit Cost (COGS) is not currently computed, causing Gross Profit to always return `available=False`.
* **Suggested Improvements:**
  - Implement dynamic currency formatting (supporting `INR` / `₹`).
  - Support `cost` column mapping so Gross Profit and Margin can be calculated when cost data is present.

---

### Module 7: Dashboard Overview & Deep-Dive Analytics UI
* **Purpose:** Provide responsive high-level KPI cards and interactive charts for commercial managers.
* **Implementation Location:** `frontend/src/pages/DashboardOverviewPage.tsx`, `AnalyticsPage.tsx`.
* **Technology Used:** React 18, Tailwind CSS, Recharts (Area, Bar charts).
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected to `/analytics/{id}` and `/summary`.
* **Test Status:** Verified in browser integration tests.
* **Known Limitations:**
  - Hardcoded `formatCurrency` uses USD.
  - Geographic map/table shows "Country" instead of "State / Region".
* **Suggested Improvements:**
  - Update table headers to "Region / State".
  - Connect centralized INR currency formatter (`₹` / Lakh / Crore).

---

### Module 8: Evidence-Grounded Three-Stage Prompt Engineering Engine
* **Purpose:** Chain 3 prompt stages (Factual Summarization $\rightarrow$ Strategic Insights $\rightarrow$ Pydantic Report) comparing v1 vs v2.
* **Implementation Location:** `backend/app/services/prompt_service.py`, `backend/app/prompts/*.jinja2`, `backend/app/services/llm_provider.py`.
* **Technology Used:** Jinja2 templates, Pydantic v2, `LocalDeterministicLLMProvider`, OpenAI/Gemini connectors.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `/prompts/execute`, `/prompts/compare`, `/prompts/templates`.
* **Test Status:** 10 tests passing in `test_prompts.py`.
* **Known Limitations:** Prompt templates currently reference generic dollars/currency in examples.
* **Suggested Improvements:** Add Indian commercial terminology, INR figures, and FMCG distributor context in prompt examples.

---

### Module 9: Deterministic Verification Engine
* **Purpose:** Catch and reject numerical hallucinations with 0.5% tolerance against Pandas ground truth.
* **Implementation Location:** `backend/app/services/verification_engine.py`.
* **Technology Used:** Regular expressions, Pydantic model validation.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Integrated into `PromptService` and `ReportService`.
* **Test Status:** Verified passing in `test_prompts.py`.
* **Known Limitations:** Regex parser expects numeric formats like `1248950.45` or `$1.25M`.
* **Suggested Improvements:** Add regex awareness for Indian numbering (`₹1.25 Lakh`, `₹12.50 Cr`).

---

### Module 10: Machine Learning Sales Forecasting
* **Purpose:** Multi-step sales forecasting with forward-shifted features, chronological holdout, and Seasonal Naive comparison.
* **Implementation Location:** `backend/app/services/forecast_service.py`.
* **Technology Used:** XGBoost Regressor, Scikit-Learn, Joblib artifact persistence.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `GET /analytics/{id}/forecast`.
* **Test Status:** 8 tests passing in `test_ml_forecast.py`.
* **Known Limitations:** Trained on Western industrial wholesale series.
* **Suggested Improvements:** Retrain and benchmark on the newly researched/generated Indian FMCG/commodity transaction series.

---

### Module 11: Machine Learning Anomaly Detection
* **Purpose:** Unsupervised transaction outlier detection with normalized [0, 1] scores and explainable pattern tags.
* **Implementation Location:** `backend/app/services/anomaly_service.py`.
* **Technology Used:** Scikit-Learn `IsolationForest`.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `GET /analytics/{id}/anomalies`.
* **Test Status:** 6 tests passing in `test_ml_anomalies.py` (100% recall on synthetic injections).
* **Known Limitations:** Contamination threshold fixed to 3.0% by default.
* **Suggested Improvements:** Benchmark on Indian FMCG transaction distributions (bulk festive orders, unusual discounts).

---

### Module 12: Business Knowledge Base & Hybrid RAG Retrieval
* **Purpose:** Ingest unstructured contracts/policies (PDF/TXT), chunk, sanitize prompt injections, and perform cosine similarity search.
* **Implementation Location:** `backend/app/services/retrieval_service.py`, `backend/app/models/knowledge.py`.
* **Technology Used:** `pypdf`, `sentence-transformers` (`all-MiniLM-L6-v2`), NumPy cosine similarity.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `/knowledge/upload`, `/knowledge/search`, `/knowledge/`.
* **Test Status:** 13 tests passing in `test_rag.py`.
* **Known Limitations:** Existing demonstration documents refer to generic Western payment terms (Net-30) and GBP/USD.
* **Suggested Improvements:** Add realistic Indian distributor policies (GST billing rules, Mandi transit terms, FMCG return policies).

---

### Module 13: Controlled LangGraph AI Business Analyst Copilot
* **Purpose:** Stateful 4-node agent executing strictly vetted tools with parameter clamping and injection defense.
* **Implementation Location:** `backend/app/services/agent_service.py`, `backend/app/models/agent.py`.
* **Technology Used:** LangGraph (`StateGraph`), Pydantic.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `/agent/chat`, `/agent/sessions`.
* **Test Status:** 13 tests passing in `test_agent.py`.
* **Known Limitations:** Quick prompt chips use generic questions.
* **Suggested Improvements:** Add India-specific commercial questions (Maharashtra revenue, FMCG product categories, GST returns).

---

### Module 14: Executive Boardroom PDF Report Generation
* **Purpose:** Multi-page audit-grade PDF generation with embedded Matplotlib charts, running headers, and metadata ribbon.
* **Implementation Location:** `backend/app/services/report_service.py`, `backend/app/models/report.py`.
* **Technology Used:** ReportLab, Matplotlib (`Agg` non-interactive backend).
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** Connected via `/reports/generate`, `/reports/{id}/download`.
* **Test Status:** 4 tests passing in `test_reports.py`.
* **Known Limitations:** Hardcodes USD (`$`) symbols in tables and chart axes.
* **Suggested Improvements:** Update currency symbol to `₹`, format using Indian numbering conventions, and brand for BharatTrade Distributors.

---

### Module 15: Progressive Web App (PWA) & Service Worker
* **Purpose:** Provide offline shell caching, mobile app installability, and fast loading for warehouse managers.
* **Implementation Location:** `frontend/public/manifest.webmanifest`, `frontend/public/sw.js`, `frontend/src/main.tsx`.
* **Technology Used:** Web App Manifest, Service Worker Cache API.
* **Working Status:** **WORKING & VERIFIED**
* **Backend Connectivity:** All `/api/` network requests bypass service worker cache for real-time freshness.
* **Test Status:** Verified in production build.
* **Known Limitations:** Background sync when offline is not yet active.
* **Suggested Improvements:** Ensure PWA icons and app name display "InsightForge AI — Indian Business Edition".

---

### Module 16: Shared Formatting Utilities & Currency Handling
* **Purpose:** Centralized formatting of currency, numbers, percentages, and bytes.
* **Implementation Location:** `frontend/src/lib/utils.ts`.
* **Technology Used:** `Intl.NumberFormat`.
* **Working Status:** **PARTIAL / NEEDS FIX**
* **Test Status:** **2 FAILING TESTS** in `frontend/src/lib/utils.test.ts`:
  1. `formatCurrency(null)` returned `"$NaN"` instead of `"$0.00"`.
  2. `formatPercentage(12.5)` returned `"12.5%"` instead of `"+12.5%"`.
* **Known Limitations:** Formatter is hardcoded to `en-US` and `USD`. Does not support `INR`, Lakhs, Crores, or Indian number grouping (`en-IN`).
* **Suggested Improvements:** Overhaul `frontend/src/lib/utils.ts` to implement robust Indian currency formatting (`en-IN`, `₹`, Lakh, Crore) with safe null handling and sign support.

---

## 3. Critical Action Items for Master Prompt 7

1. **Fix Frontend Test Regressions:** Upgrade `frontend/src/lib/utils.ts` with comprehensive null safety, sign formatting, and Indian locale support (`en-IN`, `₹`, Lakhs, Crores).
2. **Research Real Indian Business Datasets:** Investigate public Indian commercial data sources (data.gov.in, Kaggle, academic archives) and author `docs/DATASET_RESEARCH.md`.
3. **Upgrade Indian Demo Mode (BharatTrade Distributors):** Create a deterministic seeded FMCG/Wholesale generator with Indian cities, FMCG categories, INR prices, costs, cancellations, and GST assumptions.
4. **Localize Backend Analytics & Formatting:** Support `INR` / `₹`, compute Gross Profit when cost is present, and update chart labels to State/Region.
5. **Localize Knowledge Base & Agent Copilot:** Add Indian business demo documents (GST policy, distribution guidelines) and update AI Copilot quick prompts.
6. **Localize Executive PDF Reports:** Update ReportLab PDF compilation to feature INR, Indian dates, and BharatTrade branding.
7. **Complete Project Documentation:** Author `docs/PROJECT_EXPLANATION.md`, `docs/FEATURE_INVENTORY.md`, `docs/TECHNOLOGY_DECISIONS.md`, `docs/PROJECT_HISTORY.md`, and update `README.md`, `DEMO_SCRIPT.md`, and `VIVA_QUESTIONS.md`.
