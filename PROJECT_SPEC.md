# InsightForge AI — Product Specification

**Version:** 2.0.0 (Indian Business Edition)  
**Target Milestone:** Computer Science Prompt Engineering Course — Capstone Project & Production Release  
**System Class:** B2B SaaS Augmented Commercial Analytics Platform (Mobile-First PWA)

---

## 1. Executive Summary & Vision

**InsightForge AI — Indian Business Edition** is an intelligent, augmented commercial analytics SaaS platform tailored for small-to-medium wholesale distributors, FMCG super-stockists, and multi-channel retailers across India. The platform transforms raw tabular transactional records into actionable commercial intelligence, strategic diagnostic narratives, predictive forecasts, and automated boardroom PDF reports.

InsightForge AI enforces a **strict architectural boundary between deterministic computation and generative reasoning**:
> **Core Tenet:** *Never ask a Large Language Model to calculate numbers.*  
> All mathematical aggregations, KPI computations, period-over-period delta analyses, and quality metrics are computed exclusively with verified deterministic engines (Pandas/NumPy). Generative and agentic AI systems receive verified numerical artifacts as immutable evidence bounds.

---

## 2. Target Persona & Problem Statement

### 2.1 Target Persona
* **Primary:** Operations Director, Inventory Lead, and Commercial Finance Manager at B2B wholesale / FMCG distribution firms (₹5 Crore – ₹100 Crore annual turnover) in hubs like Pune, Mumbai, Nagpur, Bengaluru, Hyderabad, Delhi NCR, Ahmedabad, Chennai, and Jaipur.
* **Environment:** Frequent floor work, mobile warehouse supervision, desktop executive reviews. Needs immediate responsiveness across mobile viewports (smartphones, tablets) and high-density desktop displays.

### 2.2 Core Friction Points
1. **Spreadsheet Fragility:** Inability to reliably detect anomalies, negative quantity cancellations, or customer churn across large transaction logs (e.g. 5,000 to 50,000+ line items).
2. **Hallucination Risk in LLM Analytics:** Commercial leaders cannot trust vanilla LLM chat interfaces (ChatGPT, Claude) for quantitative decision-making due to numerical hallucinations.
3. **Data Silos:** Disconnect between tabular transactional data and enterprise knowledge (supplier contracts, credit terms, SLA agreements, GST rules).


---

## 3. Product Scope & Phased Feature Matrix

| Capability Category | Phase 1–4 (Current Scope) | Future Phases (Prompts 2–6) |
| :--- | :--- | :--- |
| **Authentication & Workspaces** | Multi-tenant workspace isolation, JWT tokens, bcrypt security, role hierarchy (Owner, Admin, Member, Viewer). | Enterprise SSO (OAuth2/SAML), audit logging, seat billing. |
| **Data Ingestion** | CSV and Excel (`.xlsx`, `.xls`) file upload, file validation, auto-detection of column roles, quality report generation. | Automated cloud sync (S3/GCS buckets, Snowflake/BigQuery connectors), webhook ingestion. |
| **Deterministic KPI Engine** | Revenue, orders, units sold, AOV, unique customers, cancellation rate, monthly growth, product and geographic ranking. | Margin & profitability calculation (when unit cost catalog is provided), cohort retention matrices. |
| **Data Quality Assurance** | Missing value detection, duplicate row auditing, cancellation invoice tagging (`C*` prefix), date parsing verification. | Automated outlier imputation, data transformation pipeline builders. |
| **Augmented Intelligence (LLM)** | Staged interfaces (`llm_provider`, `prompt_service`). Explicit placeholder signaling. | 3-stage chained evidence-grounded prompt pipeline (Diagnostic $\rightarrow$ Strategic $\rightarrow$ Executive). |
| **Predictive Machine Learning** | Staged interfaces (`forecast_service`, `anomaly_service`). | XGBoost 6-month revenue forecasting and Isolation Forest transaction anomaly detection. |
| **Document Intelligence (RAG)** | Staged interface (`retrieval_service`). | Hybrid vector search (pgvector / dense embeddings) over vendor contracts & business policies. |
| **Agentic AI** | Staged interface (`agent_service`). | LangGraph multi-step autonomous data investigation and remediation workflows. |
| **Reporting & Export** | Staged interface (`report_service`). Client-side data preview export. | Automated branded PDF report compilation with embedded SVG charts and LLM evidence footnotes. |
| **User Experience (UI/UX)** | Navy/slate/teal design system, full light/dark mode, mobile bottom navigation, desktop sidebar, live metric cards, Recharts visualizations. | Push notifications, offline PWA cache, customizable widget grids. |

---

## 4. Benchmark Dataset Specifications

### 4.1 Primary Real-World Benchmark: UCI Online Retail II
* **Source:** UCI Machine Learning Repository (Transnational transaction dataset from a UK-based registered non-store online retail).
* **Characteristics:** 1,067,371 rows across 2009–2011; contains wholesale giftware purchases by small retailers across Europe and worldwide.
* **Key Columns:** `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country`.
* **Notable Data Anomalies:** Cancellation records prefixed with 'C', negative unit quantities, zero unit prices, missing customer identifiers.

### 4.2 Synthetic Wholesale Benchmark
* Reproducible generator script located at `backend/scripts/generate_synthetic_data.py`.
* Pre-generated sample: `data/samples/synthetic_wholesale.csv` (5,015 records).
* Includes realistic distribution of products, order quantities, price ranges, European export territories, and intentional data quality test vectors (missing customer IDs, duplicate rows, cancellation invoices).

---

## 5. Security, Isolation & Compliance Requirements

1. **Workspace Boundary:** Every dataset, column metadata, and KPI calculation belongs strictly to a single `workspace_id`. Cross-workspace queries are rejected with HTTP 403 Forbidden.
2. **Password Hashing:** Directly salted via `bcrypt` (72-byte truncation boundary enforced). Plaintext passwords never persist.
3. **Stateless Authorization:** Cryptographically signed HMAC-SHA256 JWT bearer tokens containing subject identifiers and expiration timestamps.
4. **File Safety:** Upload limits capped at 50 MB per file, strict MIME and extension validation (`.csv`, `.xlsx`, `.xls`), sanitized file naming using UUID prefixes.
