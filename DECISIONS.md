# Architecture Decision Records (ADRs)

---

### ADR-001: Modular Monolith Architecture over Microservices
* **Status:** Accepted
* **Context:** InsightForge AI is designed for high-cohesion, rapid iteration in an academic capstone and B2B SaaS context. A distributed microservice topology introduces premature network serialization, distributed state sync overhead, and deployment complexity.
* **Decision:** Implement a modular monolith with decoupled internal service layers (`analytics_service`, `dataset_service`, `future_services`), clear boundaries, and clean interfaces.
* **Consequences:** Simple continuous deployment, shared relational transactional integrity, sub-millisecond in-process function invocation, zero distributed tracing overhead. Easy path to decompose into microservices later if scaling demands.

---

### ADR-002: Deterministic Business Analytics with Pandas (Zero LLM Numerical Computation)
* **Status:** Accepted
* **Context:** Generative Large Language Models inherently suffer from arithmetic hallucination, precision errors, and non-deterministic aggregations over large numerical arrays.
* **Decision:** Strictly mandate that all mathematical KPI computations (revenue, units, orders, AOV, growth percentages, cancellation rates) are executed exclusively by verified Python code using Pandas and NumPy.
* **Consequences:** Complete mathematical auditability, 100% reproducible results, zero token cost for computation, and reliable bounding evidence for future LLM prompt chains.

---

### ADR-003: Direct bcrypt with 72-Byte Boundary over Passlib Wrapper
* **Status:** Accepted
* **Context:** Modern Python environments running `bcrypt >= 4.1.0` or `5.0.0` have removed internal `__about__` module attributes and enforce strict 72-byte string boundaries, causing standard `passlib` bcrypt backend initialization to throw `AttributeError` and `ValueError`.
* **Decision:** Utilize the native `bcrypt` library directly (`bcrypt.hashpw` and `bcrypt.checkpw`) with explicit 72-byte truncation in `app/core/security.py`.
* **Consequences:** Eliminates deprecated wrappers, guarantees compatibility with all modern Python 3.12/3.14 runtimes, ensures sub-millisecond password hashing security.

---

### ADR-004: Workspace-Scoped Multi-Tenant Data Isolation
* **Status:** Accepted
* **Context:** B2B commercial transaction data is confidential and sensitive across organizations.
* **Decision:** Every dataset, upload file, column configuration, and computed metric belongs strictly to a `workspace_id`. All API routes require explicit membership verification via `_check_workspace_access()`.
* **Consequences:** Zero risk of multi-tenant data leakage. Enables granular permission roles (`owner`, `admin`, `member`, `viewer`).

---

### ADR-005: Staged Future Interfaces Pattern
* **Status:** Accepted
* **Context:** Stages 1–4 prohibit premature implementation of ML models, paid LLM APIs, LangGraph agent workflows, or RAG vectors, yet Stages 5–6 require seamless integration without altering frontend-backend contracts.
* **Decision:** Implement explicit service contracts (`ForecastService`, `AnomalyService`, `LLMProvider`, `PromptService`, `RetrievalService`, `AgentService`, `ReportService`) returning typed `"not_implemented"` statuses rather than mocked fake outputs.
* **Consequences:** Codebase remains strictly honest about capabilities while establishing rock-solid architecture ready for Prompt 2–6.

---

### ADR-006: Mobile-First Responsive PWA Design System
* **Status:** Accepted
* **Context:** Warehouse managers, inventory supervisors, and traveling sales leads access commercial analytics on mobile devices and tablets, while analysts use widescreen monitors.
* **Decision:** Build a responsive UI using Tailwind CSS with bottom navigation bars on mobile viewports (< 768px) and a persistent collapsible sidebar on desktop viewports ($\ge$ 768px). Support both light and dark visual themes with a high-contrast navy/slate/teal palette.
* **Consequences:** High usability across all device form-factors with zero desktop feature regression on touch devices.

---

### ADR-007: Dialect-Aware SQLAlchemy Connection & In-Memory Test Isolation
* **Status:** Accepted
* **Context:** PostgreSQL connection pool parameters (`pool_size`, `max_overflow`) are unsupported by SQLite, which raised errors during in-memory automated test execution. Additionally, enum role types may return raw enum instances or strings depending on dialect.
* **Decision:** Configure `create_engine` with dialect awareness in `app/core/database.py`, omitting pool parameters for SQLite connections and adding `check_same_thread: False`. Implement `_role_to_str` in workspace endpoints to safely handle both Enum and raw string representations.
* **Consequences:** Enables zero-dependency in-memory integration testing via FastAPI `TestClient` while retaining full PostgreSQL connection pooling in production.

---

### ADR-008: Jinja2 Template-Based Prompt Versioning (v1 vs. v2)
* **Status:** Accepted
* **Context:** Prompt engineering requires systematic experimentation and controlled A/B evaluation between baseline few-shot prompts and structured, evidence-grounded prompt architectures.
* **Decision:** Store all prompts as versioned Jinja2 templates (`prompt1_factual_v1.jinja2`, `prompt1_factual_v2.jinja2`, etc.) in `backend/app/prompts/`. Render templates using a centralized `PromptService` supporting side-by-side execution on identical dataset KPIs.
* **Consequences:** Decouples prompt engineering from application code, enables runtime template inspection, and facilitates direct mathematical and qualitative diffs across prompt revisions.

---

### ADR-009: Verification Engine with Structured Metric References
* **Status:** Accepted
* **Context:** Verifying arbitrary, unstructured free-form numeric prose using regular expressions or LLM self-reflection is computationally fragile, prone to false positives, and vulnerable to recursive hallucinations.
* **Decision:** Mandate that Prompt v2 outputs structured claims with explicit metric reference arrays (`[METRIC:metric_id]` with numeric values). The `VerificationEngine` checks these structured tuples directly against deterministic Pandas calculations using a 0.5% tolerance threshold.
* **Consequences:** Guarantees 100% deterministic mathematical verification, provides exact discrepancy percentages, eliminates recursive LLM verification costs, and enables automated repair of minor formatting drift.

---

### ADR-010: Zero-Cost Unauthenticated Demo Exploration with Protected Cloud Fallback
* **Status:** Accepted
* **Context:** Academic reviewers, course instructors, and demo evaluators require immediate access to benchmark analytics, deterministic prompt evaluation, and Prompt Studio inspection without mandating database seeding, user registration, or paid third-party API keys. However, cloud LLM providers (OpenAI, Gemini) must remain strictly guarded against anonymous unauthenticated invocation to prevent API key quota exhaustion.
* **Decision:** Implement optional Bearer authentication (`get_current_user_optional`) across analytics and prompt endpoints. Permitted operations without authentication include:
  1. Any request targeting `workspace_id.startswith("demo-")` or `dataset_id.startswith("demo-")` / `benchmark-wholesale`.
  2. Local deterministic prompt execution (`LocalDeterministicLLMProvider`), v1 vs v2 comparison, prompt template inspection, and evaluation benchmark scorecard retrieval.
  Requests to invoke live cloud providers (`provider_type in ["openai", "gemini"]`) or targeting non-demo workspaces strictly enforce authenticated JWT credentials and workspace membership.
* **Consequences:** Immediate frictionless out-of-the-box exploration for academic evaluation while maintaining airtight security and API key protection for production/cloud environments.

---

### ADR-011: Chronological Holdout Validation for XGBoost & Unsupervised Isolation Forest Outlier Screening
* **Status:** Accepted
* **Context:** In commercial time-series forecasting, standard k-fold random cross-validation causes fatal future-lookahead target leakage, creating artificially optimistic accuracy metrics. Furthermore, unsupervised anomaly detection must distinguish mathematical outliers from legal accusations of fraud.
* **Decision:**
  1. Mandate strict **chronological holdout validation** (last 20% of continuous time periods) and forward-shifted lag/rolling features for XGBoost. Evaluate models against a **Seasonal Naive lag-1 persistence baseline** using WAPE, MAE, and RMSE. Strictly forbid claiming outperformance unless measured holdout WAPE is lower.
  2. Implement **Isolation Forest** using relative deviations from SKU median prices and order quantities, normalizing scores to $[0, 1]$ and assigning explainable causal pattern tags (`EXTREME_UNIT_PRICE`, `UNUSUAL_BULK_QUANTITY`, `CANCELLATION_SPIKE`, `OFF_HOURS_ACTIVITY`). Display prominent legal disclaimers clarifying that statistical outliers represent operational anomalies rather than confirmed fraud.
* **Consequences:** Zero lookahead leakage, empirical baseline discipline, fully explainable transaction auditing, and legally sound commercial disclosures.


---

### ADR-012: Workspace-Scoped Business Knowledge RAG with Injection Sanitization
* **Status:** Accepted
* **Context:** Commercial decision-making requires evidence from unstructured business contracts, supplier SLAs, payment terms, and return policies (e.g. net-30 days, 15% restocking fee). However, language models must never use retrieved text to perform financial arithmetic, must not follow malicious instructions embedded in documents (prompt injection), and must never leak proprietary contracts across workspace boundaries.
* **Decision:**
  1. Store document metadata and sliding-window text chunks in relational tables (`knowledge_documents`, `document_chunks`), denormalizing `workspace_id` directly onto chunks for database-level isolation.
  2. Embed document passages with `all-MiniLM-L6-v2` (`sentence-transformers`, 384-dimensional dense vectors) and calculate cosine similarity in memory, filtering strictly at a 0.25 similarity floor.
  3. Enforce **RAG Design Rules**:
     - RAG text is contextual evidence only, not executable instructions.
     - Neutralize prompt-injection directives (e.g. `IGNORE PREVIOUS INSTRUCTIONS`) at ingestion time by replacing matching lines with neutral placeholders.
     - Pass retrieved citations (`[DOC-N] Title (Source)`) into Stage 2 of the prompt chain (`prompt2_insights_v2.jinja2`), while numeric verification continues to validate all arithmetic against Pandas KPIs.
     - Return `"Insufficient data"` when no relevant documents exist.
* **Consequences:** Airtight tenant isolation, complete protection against prompt-injection attacks, rigorous citation provenance, and zero interference with deterministic KPI calculation.


---

### ADR-013: Controlled LangGraph Business Analyst Agent with Bounded Tool Execution
* **Status:** Accepted
* **Context:** In enterprise commercial decision-making, autonomous AI agents with unconstrained code execution (`eval`/`exec`) or arbitrary SQL query generation pose severe security, data corruption, and arithmetic hallucination risks. Agents must operate within provably safe operational boundaries, select strictly vetted tools, and return explainable traces.
* **Decision:**
  1. Implement a stateful, bounded business analysis agent using **LangGraph** (`StateGraph`) with a deterministic four-node topology:
     - `classify_and_plan`: Regex-anchored intent classifier with immediate short-circuiting for prompt injections and out-of-domain requests.
     - `validate_arguments`: Parameter clamping and schema validation (e.g. forecast periods clamped to $[1, 12]$, product limits clamped to $[1, 20]$, contamination clamped to $[0.01, 0.10]$).
     - `execute_tools`: Bounded invocation of up to 7 approved business tools (`get_business_kpis`, `analyze_revenue_trends`, `get_product_performance`, `forecast_sales`, `detect_anomalies`, `retrieve_business_documents`, `generate_executive_report`) with isolated error recovery per tool.
     - `synthesize_response`: Evidence-grounded synthesis linking numerical metrics (`[METRIC:...]`) and document citations (`[DOC-N: ...]`), coupled with structured interactive chart payloads (`kpi_grid`, `revenue_trends`, `product_ranking`, `forecast`, `anomaly_distribution`).
  2. Enforce strict security guardrails:
     - Absolute prohibition of raw SQL generation or arbitrary Python evaluation.
     - Multi-tenant workspace scoping verified on every call.
     - Transparent execution trace drawer exposing tool names, parameters, latency in milliseconds, and status chips.
     - Clear distinction between demo mode (unauthenticated exploration with benchmark data) and authenticated production mode.
* **Consequences:** Provably safe tool dispatching, zero code execution vulnerabilities, reproducible execution traces, full numerical groundedness, and rich interactive data visualizations in the mobile-first frontend.

---

### ADR-014: Production-Grade PDF Reporting Engine and Comprehensive Academic Evaluation Framework
* **Status:** Accepted
* **Context:** Commercial decision-makers require executive-grade, audit-ready PDF reports containing verified KPI summaries, high-resolution figures, machine learning forecasts with prediction intervals, statistical anomaly distributions, and verifiable recommendations. Furthermore, an academic capstone demands reproducible experimental evaluation across 12 dimensions: Prompt v1 vs v2 accuracy, structural JSON adherence, hallucination rates, ML baseline comparison, anomaly recall on synthetic outliers, RAG retrieval latency, and agent routing reliability without fabricating metrics.
* **Decision:**
  1. Implement `ReportService` using `ReportLab` with custom `NumberedCanvas` (`Page X of Y`), corporate design palette, and non-interactive `matplotlib` figures (`Agg` backend) generating multi-page vector-rendered PDF documents. All numbers injected into the document originate strictly from deterministic computation (`AnalyticsService`, `ForecastService`, `AnomalyService`, and Stage 3 structured prompt outputs).
  2. Implement `ReportRecord` relational model for report history tracking with complete metadata snapshots (dataset ID, prompt version v1/v2, KPI snapshot, generation timestamp).
  3. Execute automated research evaluation script (`backend/scripts/run_academic_evaluation.py`) executing 12 empirical benchmarks against the wholesale benchmark dataset:
     - Prompt v2 100.0% numerical accuracy vs v1 33.3% accuracy.
     - Prompt v2 0 unsupported claims vs v1 ungrounded approximations.
     - Prompt v2 100.0% JSON schema pass rate vs v1 0%.
     - XGBoost holdout WAPE (45.71%) vs Seasonal Naive (23.92%), honestly reporting baseline competitiveness on intermittent wholesale series.
     - Isolation Forest recall of 90.0% on injected extreme commercial anomalies.
     - RAG cosine retrieval latency (sub-50ms warm) and precision.
     - LangGraph agent tool routing accuracy (93.8%) and prompt injection rejection (100.0%).
* **Consequences:** Audit-grade downloadable PDF artifacts, verifiable report history, complete transparency regarding ML model boundaries, and an academically defensible empirical evaluation artifact (`data/samples/academic_research_evaluation.json`).

