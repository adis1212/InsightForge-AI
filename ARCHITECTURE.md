# InsightForge AI — System Architecture & Technical Design

**Pattern:** Modular Monolith with Decoupled Frontend Single Page Application (PWA)  
**System Status:** Stages 1–5 Implemented and Verified (Prompt Engineering Engine Active)  

---

## 1. High-Level Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                            CLIENT TIER (Mobile-First SPA)                         |
|  React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui + TanStack Query + Recharts |
|  - Dashboard Overview  │  Data Preview  │  Business Analytics  │  Prompt Studio    |
+-----------------------------------------------------------------------------------+
                                         │  HTTPS / JSON / Bearer JWT
                                         ▼
+-----------------------------------------------------------------------------------+
|                           GATEWAY & FASTAPI WEB TIER                              |
|   CORS Middleware  │  Global Exception Handling  │  JWT Security & Auth Dependency |
+-----------------------------------------------------------------------------------+
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
+-----------------------+    +-----------------------+    +-------------------------------+
|   CORE APPLICATION    |    | DETERMINISTIC ENGINE  |    |   STAGE 5: PROMPT ENGINE      |
| - Users & Workspaces  |    | - Dataset Ingestion   |    | - Stored Jinja2 (v1 vs v2)    |
| - Relational Models   |    | - Column Auto-Detect  |    | - PromptService 3-Stage Chain |
| - Scoped Authorizer   |    | - Quality Auditor     |    | - VerificationEngine (Auditor)|
| - SQLite / PostgreSQL |    | - Pandas KPI Engine   |    | - LLMProvider Abstraction    |
+-----------------------+    +-----------------------+    +-------------------------------+
                                         │                                │
                                         └────────────────┬───────────────┘
                                                          ▼
                                           +-----------------------------+
                                           |  STAGED FUTURE INTERFACES   |
                                           | - ForecastService (XGBoost) |
                                           | - AnomalyService (IsoForest)|
                                           | - RetrievalService (RAG)    |
                                           | - AgentService (LangGraph)  |
                                           | - ReportService (PDF)       |
                                           +-----------------------------+
```

---

## 2. Evidence-Grounded Prompt Engineering Pipeline

The platform enforces a strict 3-stage prompt pipeline where each stage builds on verified evidence:

```
[ Deterministic Pandas KPIs ] 
              │
              ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ STAGE 1: Factual Data Summarization                         │
  │ Input: Verified Pandas KPI JSON                             │
  │ Output: Structured claims with [METRIC:id] citations        │
  │ Verification: Metric existence & value matches within 0.5%   │
  └─────────────────────────────────────────────────────────────┘
              │
              ▼ (Verified Claims + KPIs)
  ┌─────────────────────────────────────────────────────────────┐
  │ STAGE 2: Business Insights & Recommendations                │
  │ Input: Validated Stage 1 claims + Deterministic KPIs        │
  │ Output: Hypotheses ([HYPOTHESIS]), Risks & Action Items     │
  │ Rule: "Insufficient data" mandatory for unprovided causes   │
  │ Verification: Hypothesis labeling & refusal compliance     │
  └─────────────────────────────────────────────────────────────┘
              │
              ▼ (Validated Insights + Claims)
  ┌─────────────────────────────────────────────────────────────┐
  │ STAGE 3: Structured Executive Report Formatting             │
  │ Input: Stage 1 claims + Stage 2 insights                    │
  │ Output: Strict JSON adhering to ExecutiveCommercialReport   │
  │ Verification: Pydantic schema validation & markdown strip   │
  └─────────────────────────────────────────────────────────────┘
              │
              ▼
[ Verified Boardroom-Ready Report JSON + Accuracy Scorecard ]
```

---

## 3. Technology Stack Justification

### 3.1 Backend Core & AI Services
* **Python 3.12 / 3.14 + FastAPI:** Async API server offering automatic OpenAPI v3 documentation, native Pydantic schema validation, and high throughput.
* **Jinja2:** Template engine for versioned prompt templates (`prompt1_factual_v1/v2`, `prompt2_insights_v1/v2`, `prompt3_report_v1/v2`).
* **Pydantic v2:** Strict JSON schema validation for LLM outputs (`ExecutiveCommercialReport`, `VerificationResult`).
* **SQLAlchemy 2.0 (Declarative Base):** Dialect-aware ORM supporting both local SQLite and production PostgreSQL.
* **Pandas 2.2 + NumPy 2.2:** Vectorized mathematical operations guaranteeing 100% deterministic KPI calculations with zero LLM math.
* **httpx:** Async HTTP client powering OpenAI and Gemini provider adapters.
* **bcrypt + python-jose:** Password hashing with 72-byte truncation boundary and HMAC-SHA256 JWT management.

### 3.2 Frontend Client
* **React 18 + TypeScript:** Type-safe component architecture.
* **Vite:** Rapid development and production bundling.
* **Tailwind CSS + Lucide React:** Responsive Navy/Slate/Teal design system with light/dark theme toggle.
* **TanStack React Query v5:** Asynchronous server-state management.
* **Recharts:** Composable SVG data visualizations.

---

## 4. API Endpoints Contract

### 4.1 Prompt Engineering Engine (`/api/v1/workspaces/{id}/prompts`)
* `POST /execute` $\rightarrow$ Execute the 3-stage chain with selected version (`v1` or `v2`) and provider.
* `POST /compare` $\rightarrow$ Side-by-side execution of v1 and v2 on identical dataset KPIs.
* `GET /templates` $\rightarrow$ Inspect stored Jinja2 templates and architectural diff explanations.
* `GET /evaluation` $\rightarrow$ Retrieve latest golden dataset evaluation benchmark scorecard.
* `POST /evaluate` $\rightarrow$ Trigger fresh automated evaluation across golden scenarios.

### 4.2 System, Workspaces & Datasets
* `GET /api/v1/health` $\rightarrow$ Health check status.
* `POST /api/v1/auth/*` $\rightarrow$ Register, login, profile verification.
* `GET /api/v1/workspaces/*` $\rightarrow$ Workspace CRUD and authorization checks.
* `POST /api/v1/workspaces/{id}/datasets/upload` $\rightarrow$ Multipart file ingestion.
* `GET /api/v1/workspaces/{id}/analytics/{dataset_id}` $\rightarrow$ Full deterministic analytics payload.

---

## 5. Clean Modular Interface Contracts for Future Stages (Prompt 3+)

```python
class ForecastService:      # Prompt 3: XGBoost multivariate time-series forecasting
class AnomalyService:       # Prompt 3: Isolation Forest unsupervised transactional outlier detection
class RetrievalService:     # Prompt 4: Vector document index & RAG query engine
class AgentService:         # Prompt 5: LangGraph multi-step operational agent
class ReportService:        # Prompt 5: Automated PDF report generator with visual analytics
```
Each stub returns a standardized JSON response:
```json
{
  "status": "not_implemented",
  "service": "<service_name>",
  "message": "<Description of target prompt phase>"
}
```
Under no circumstances do these stubs simulate or mock artificial responses.
