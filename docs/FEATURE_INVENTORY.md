# InsightForge AI — Comprehensive Feature Inventory

**Document Purpose:** Exhaustive System Feature Catalog & Audit Record  
**Version:** 2.0 (Indian Business Edition)  
**Last Updated:** November 18, 2026  

---

## 1. Feature Catalog

### Feature 1: Multi-Tenant JWT Authentication & RBAC
* **Purpose:** Secure user registration, authentication, token management, and profile access.
* **Why Needed:** Commercial transaction data is confidential and sensitive across different businesses; cross-tenant access must be prevented at the database level.
* **Technology Used:** FastAPI, SQLAlchemy 2.0, JWT (HMAC-SHA256), native `bcrypt` (with 72-byte truncation boundary).
* **Backend Location:** `backend/app/api/v1/endpoints/auth.py`, `backend/app/core/security.py`, `backend/app/models/user.py`.
* **Frontend Location:** `frontend/src/pages/AuthPage.tsx`, `frontend/src/context/AuthContext.tsx`.
* **API Endpoints:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`.
* **User-Visible Behavior:** Clean sign-in / registration modal with password confirmation, demo mode bypass button, and user avatar dropdown.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 6 dedicated unit tests in `test_security.py`; full registration and login flow in `test_api_integration.py`.
* **Known Limitations:** Password reset via email is omitted in local scope.

---

### Feature 2: Workspace Management & Data Isolation
* **Purpose:** Create, list, switch, and isolate multi-tenant commercial organizations.
* **Why Needed:** Allows a business owner or consultant to manage multiple business accounts (e.g., Pune Wholesale Hub, Bangalore Retail) without data overlap.
* **Technology Used:** PostgreSQL / SQLite relational models with `WorkspaceMember` association table.
* **Backend Location:** `backend/app/api/v1/endpoints/workspaces.py`, `backend/app/models/workspace.py`.
* **Frontend Location:** `frontend/src/pages/WorkspacePage.tsx`, `frontend/src/components/layout/Navbar.tsx` (Workspace Switcher).
* **API Endpoints:** `GET /api/v1/workspaces/`, `POST /api/v1/workspaces/`, `GET /api/v1/workspaces/{id}`, `PUT /api/v1/workspaces/{id}`, `DELETE /api/v1/workspaces/{id}`.
* **User-Visible Behavior:** Organization switcher in top navigation bar; workspace management dashboard displaying member roles (`owner`, `admin`, `member`).
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** Multi-tenant 403 Forbidden verification tests in `test_api_integration.py` and `test_e2e_journey.py`.
* **Known Limitations:** Workspace invitations are currently managed locally via direct role assignments.

---

### Feature 3: Tabular Dataset Ingestion & Validation
* **Purpose:** Multi-format file ingestion supporting CSV and Excel files bounded to 50 MB.
* **Why Needed:** Commercial sales ledgers are distributed in diverse formats with irregular naming conventions.
* **Technology Used:** `pandas`, `openpyxl`, `xlrd`, FastAPI multipart streaming.
* **Backend Location:** `backend/app/api/v1/endpoints/datasets.py`, `backend/app/services/dataset_service.py`.
* **Frontend Location:** `frontend/src/pages/DatasetUploadPage.tsx`.
* **API Endpoints:** `POST /api/v1/workspaces/{id}/datasets/upload`, `GET /api/v1/workspaces/{id}/datasets/`, `GET /api/v1/workspaces/{id}/datasets/{id}`.
* **User-Visible Behavior:** Drag-and-drop file upload zone with animated progress indicator, size check badge, and format filter.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 15 passing tests in `test_dataset_service.py` verifying oversized rejection (>50 MB) and extension filters.
* **Known Limitations:** In-memory DataFrame conversion is performed upon upload.

---

### Feature 4: Automated Column Role Detection & Mapping Override
* **Purpose:** Automatically detect canonical business roles (`invoice_no`, `stock_code`, `description`, `quantity`, `unit_price`, `unit_cost`, `customer_id`, `country`/`state`, `date`).
* **Why Needed:** Wholesale distributors use differing column names (e.g. `Bill No`, `Rate`, `MRP`, `COGS`, `Mandi`).
* **Technology Used:** Regex fuzzy string pattern matching against curated commercial synonym dictionaries.
* **Backend Location:** `backend/app/services/dataset_service.py` (`detect_column_roles`).
* **Frontend Location:** `frontend/src/pages/DatasetPreviewPage.tsx`.
* **API Endpoints:** `GET /api/v1/workspaces/{id}/datasets/{id}/preview`, `PUT /api/v1/workspaces/{id}/datasets/{id}/mapping`.
* **User-Visible Behavior:** Interactive dropdown selectors on dataset preview table allowing users to override detected roles.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** Unit tests in `test_dataset_service.py` covering standard, uppercase, spaced, and alternate column headers.
* **Known Limitations:** Highly irregular non-tabular spreadsheets require column normalization prior to upload.

---

### Feature 5: Data Quality Auditor & Hygiene Scoring
* **Purpose:** Automated pre-analytics health audit computing a quality score (0–100) and flagging data issues.
* **Why Needed:** Prevents garbage-in, garbage-out in downstream ML and AI prompt synthesis.
* **Technology Used:** Vectorized Pandas null, duplicate, date, and cancellation auditors.
* **Backend Location:** `backend/app/services/dataset_service.py` (`audit_data_quality`).
* **Frontend Location:** `frontend/src/pages/DatasetPreviewPage.tsx` (Quality Tab).
* **API Endpoints:** `GET /api/v1/workspaces/{id}/datasets/{id}/quality`.
* **User-Visible Behavior:** Circular quality score meter (e.g. 85/100), severity breakdown pills, duplicate count, null rates, and cancellation count.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** Verified passing in `test_dataset_service.py`.
* **Known Limitations:** Does not validate postal code boundaries across states.

---

### Feature 6: Deterministic Commercial KPI Engine
* **Purpose:** Compute 100% of numerical KPIs deterministically using Pandas (Zero LLM arithmetic).
* **Why Needed:** Guarantees absolute mathematical auditability and eliminates AI arithmetic hallucination.
* **Technology Used:** Vectorized Pandas and NumPy operations with division-by-zero guards.
* **Backend Location:** `backend/app/services/analytics_service.py`.
* **Frontend Location:** `frontend/src/pages/DashboardOverviewPage.tsx`, `frontend/src/pages/AnalyticsPage.tsx`.
* **API Endpoints:** `GET /api/v1/workspaces/{id}/analytics/{id}`, `GET /api/v1/workspaces/{id}/analytics/{id}/summary`.
* **User-Visible Behavior:** Responsive 6-card KPI grid (Net Revenue, Unique Orders, Units Sold, AOV, Unique Customers, Cancellation Rate) with growth badges.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 14 unit tests in `test_analytics.py` verifying revenue exclusion of cancellations and mathematical identities.
* **Known Limitations:** Gross margin is available only when unit costs are supplied; returns explicit refusal when cost is absent.

---

### Feature 7: Deep-Dive Business Analytics & Leaderboards
* **Purpose:** Visual analysis of monthly revenue growth timelines, top products by revenue and volume, and regional state rankings.
* **Why Needed:** Enables inventory managers and regional sales supervisors to identify high-velocity SKUs and geographic hubs.
* **Technology Used:** Recharts (Interactive Area and Bar charts), Tailwind CSS.
* **Backend Location:** `backend/app/services/analytics_service.py` (`calculate_monthly_revenue`, `calculate_top_products`, `calculate_geographic_performance`).
* **Frontend Location:** `frontend/src/pages/AnalyticsPage.tsx`.
* **API Endpoints:** `GET /api/v1/workspaces/{id}/analytics/{id}`.
* **User-Visible Behavior:** Monthly revenue timeline with growth rate pills; top product leaderboard with progress bars; state/regional distribution table.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** Tested in `test_analytics.py` and frontend Vitest suite.
* **Known Limitations:** Geographic breakdown groups by state/city column; choropleth GIS map rendering is planned for future releases.

---

### Feature 8: XGBoost Sales Forecasting Engine
* **Purpose:** Multi-step recursive time-series sales forecasting with 95% confidence intervals and Seasonal Naive baseline comparison.
* **Why Needed:** Helps distributors plan inventory procurement and avoid stockouts during festive peaks.
* **Technology Used:** XGBoost Regressor, Scikit-Learn, Joblib artifact persistence.
* **Backend Location:** `backend/app/services/forecast_service.py`.
* **Frontend Location:** `frontend/src/pages/MLIntelligencePage.tsx`.
* **API Endpoints:** `GET /api/v1/workspaces/{id}/analytics/{id}/forecast?periods=6`.
* **User-Visible Behavior:** Interactive chart showing observed historical actuals, XGBoost projected trajectory, 95% confidence band, and naive baseline line with WAPE scorecard.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 8 unit tests in `test_ml_forecast.py` verifying chronological holdout validation and zero target leakage.
* **Known Limitations:** Intermittent wholesale demand on short historical series can favor naive baselines; explicitly disclosed in UI.

---

### Feature 9: Isolation Forest Anomaly Detection
* **Purpose:** Unsupervised transaction outlier screening with normalized [0, 1] severity scores and explainable pattern tags.
* **Why Needed:** Detects billing typos (100x price entry errors), unusual bulk hoarding, off-hours activity, and cancellation clusters.
* **Technology Used:** Scikit-Learn `IsolationForest`, NumPy feature matrix.
* **Backend Location:** `backend/app/services/anomaly_service.py`.
* **Frontend Location:** `frontend/src/pages/MLIntelligencePage.tsx`.
* **API Endpoints:** `GET /api/v1/workspaces/{id}/analytics/{id}/anomalies?contamination=0.03`.
* **User-Visible Behavior:** Score distribution histogram, severity breakdown pills (Critical, High, Medium, Low), and searchable flagged transactions table.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 6 unit tests in `test_ml_anomalies.py` demonstrating 100% recall on synthetic injected outliers.
* **Known Limitations:** Flags statistical deviations; requires human commercial verification before action.

---

### Feature 10: Business Document Ingestion & Hybrid RAG Retrieval
* **Purpose:** Ingest unstructured contracts/SLAs (PDF/TXT), chunk text, sanitize prompt injections, and perform cosine similarity search.
* **Why Needed:** Provides contextual policy evidence (e.g. payment terms, return policies, restocking fees) to ground AI recommendations.
* **Technology Used:** `pypdf`, `sentence-transformers` (`all-MiniLM-L6-v2`), NumPy in-memory cosine similarity.
* **Backend Location:** `backend/app/services/retrieval_service.py`, `backend/app/models/knowledge.py`.
* **Frontend Location:** `frontend/src/pages/KnowledgeBasePage.tsx`.
* **API Endpoints:** `POST /api/v1/workspaces/{id}/knowledge/upload`, `GET /api/v1/workspaces/{id}/knowledge/`, `POST /api/v1/workspaces/{id}/knowledge/search`, `DELETE /api/v1/workspaces/{id}/knowledge/{id}`.
* **User-Visible Behavior:** Drag-and-drop document upload, indexed document list with chunk badges, semantic search tester with similarity score bars.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 13 unit tests in `test_rag.py` verifying multi-tenant isolation, similarity floor (0.25), and prompt injection neutralization.
* **Known Limitations:** In-memory dense vector search is optimized for SME libraries (<1,000 documents).

---

### Feature 11: Controlled LangGraph AI Business Analyst Copilot
* **Purpose:** Conversational commercial copilot executing strictly vetted tools within bounded graph states.
* **Why Needed:** Allows business owners to ask questions in plain language without risking arbitrary code or SQL execution.
* **Technology Used:** LangGraph (`StateGraph`), Pydantic v2 schemas, Jinja2 prompt engine.
* **Backend Location:** `backend/app/services/agent_service.py`, `backend/app/models/agent.py`.
* **Frontend Location:** `frontend/src/pages/AICopilotPage.tsx`.
* **API Endpoints:** `POST /api/v1/workspaces/{id}/agent/chat`, `GET /api/v1/workspaces/{id}/agent/sessions`, `GET /api/v1/workspaces/{id}/agent/sessions/{id}`.
* **User-Visible Behavior:** Interactive chat interface with quick-launcher prompt chips, collapsible tool execution trace drawer, inline interactive Recharts, and clickable evidence badges.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 13 unit tests in `test_agent.py` covering tool selection, bounds clamping, prompt injection defense, and unsupported domain fallbacks.
* **Known Limitations:** Operates in offline deterministic mode when external cloud LLM API keys are not supplied.

---

### Feature 12: Boardroom Executive PDF Report Generator
* **Purpose:** Multi-page audit-grade PDF generation with embedded high-DPI Matplotlib charts, running headers, and metadata ribbon.
* **Why Needed:** Delivers formal, verifiable reporting artifacts for executive leadership, investors, and bank loan applications.
* **Technology Used:** ReportLab, custom `NumberedCanvas` (`Page X of Y`), Matplotlib (`Agg` backend).
* **Backend Location:** `backend/app/services/report_service.py`, `backend/app/models/report.py`.
* **Frontend Location:** `frontend/src/pages/ReportsPage.tsx`.
* **API Endpoints:** `POST /api/v1/workspaces/{id}/reports/generate`, `GET /api/v1/workspaces/{id}/reports/`, `GET /api/v1/workspaces/{id}/reports/{id}/download`, `DELETE /api/v1/workspaces/{id}/reports/{id}`.
* **User-Visible Behavior:** Report generation modal with prompt version toggle, history table with status badges, in-browser JSON audit inspector, and direct PDF download button.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 4 unit tests in `test_reports.py` checking structural PDF generation, text extraction with `pypdf`, and REST endpoints.
* **Known Limitations:** PDF compilation takes ~1.5–2.5 seconds due to Matplotlib rasterization.

---

### Feature 13: Progressive Web App (PWA) & Service Worker
* **Purpose:** Offline UI shell availability, mobile app installability, and fast asset caching for warehouse supervisors.
* **Why Needed:** Warehouse environments often have spotty mobile network connections.
* **Technology Used:** Web App Manifest (`manifest.webmanifest`), Service Worker Cache API (`sw.js`).
* **Backend Location:** N/A (Static delivery).
* **Frontend Location:** `frontend/public/manifest.webmanifest`, `frontend/public/sw.js`, `frontend/src/main.tsx`.
* **API Endpoints:** N/A (All `/api/` network requests bypass service worker cache).
* **User-Visible Behavior:** "Install App" browser prompt on mobile viewports; instant load times on repeat visits.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** Verified via clean Vite production build and browser DevTools service worker registration.
* **Known Limitations:** Background dataset synchronization when completely offline is not yet implemented.

---

### Feature 14: Centralized Indian Rupee (INR) & Locale Formatter
* **Purpose:** Centralized, locale-aware formatting for Indian currency (Lakhs and Crores), numbers, percentages, and dates (DD/MM/YYYY).
* **Why Needed:** Indian commercial users expect standard Indian numbering conventions (`₹1,25,000`, `₹12.50 Lakh`, `₹1.25 Cr`).
* **Technology Used:** `Intl.NumberFormat` (`en-IN` locale).
* **Backend Location:** `backend/app/services/analytics_service.py` (`_fmt_currency`).
* **Frontend Location:** `frontend/src/lib/utils.ts` (`formatINR`, `formatIndianCompact`, `formatIndianDate`).
* **API Endpoints:** N/A.
* **User-Visible Behavior:** All monetary cards and charts display `₹` symbols with Indian numbering conventions.
* **Real / Demo / Placeholder Status:** **100% Real Implementation**.
* **Verification Evidence:** 7 unit tests passing in `frontend/src/lib/utils.test.ts`.
* **Known Limitations:** Non-INR datasets retain their native currency to prevent misleading conversions.
