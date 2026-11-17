# InsightForge AI — Comprehensive Project History & Evolution

**Document Purpose:** Factual Chronicle of Development Phases, Architectural Decisions, Challenges, and Resolutions  
**Source Evidence:** Git Version History, Architectural Decision Records (ADR-001 through ADR-015), and `PROGRESS.md` Audit Records  
**Last Updated:** November 18, 2026  

---

## 1. Project Genesis & Initial Vision

InsightForge AI was conceived as an academic capstone and B2B SaaS research platform for Third-Year Computer Science Prompt Engineering. 

The original problem hypothesis was formulated around SME commercial decision-making:
> *"Can a modern B2B analytics platform harness the strategic narrative and summarization capabilities of Large Language Models without inheriting their fatal weaknesses—namely arithmetic hallucination, structural instability, and susceptibility to adversarial prompt injections?"*

From Day 1, the foundational architectural decision (**ADR-002: Deterministic Business Analytics with Pandas**) established that:
- Zero mathematical calculations would ever be performed by generative models.
- All KPIs would be calculated deterministically in Python (Pandas/NumPy).
- Generative models would operate strictly as narrative compilers within immutable numerical boundaries.

---

## 2. Chronological Development Milestones

### Phase 1: Full-Stack Foundation & Deterministic Analytics Engine (Stages 1–4)
* **Scope:** Backend modular monolith, multi-tenant database models, file upload pipeline, column auto-detector, and React dashboard.
* **Key Integrations:**
  - FastAPI modular directory structure with global error handling (`InsightForgeException`).
  - SQLAlchemy 2.0 relational models with multi-tenant workspace isolation (`_check_workspace_access`).
  - Native `bcrypt` implementation with explicit 72-byte truncation boundaries, eliminating deprecation errors from `passlib`.
  - Tabular file reader supporting CSV and Excel spreadsheets up to 50 MB.
  - Vectorized Pandas KPI engine computing net revenue (strictly excluding cancellation invoices), unique orders, AOV, units sold, and period-over-period monthly revenue timelines.
  - React 18 / Tailwind CSS dashboard with responsive desktop sidebar and mobile bottom navigation bar (`BottomNav.tsx`).
* **Test Milestone:** 42 initial foundation and unit tests verified passing.

---

### Phase 2: Evidence-Grounded Prompt Engineering Engine (Stage 5)
* **Scope:** Decoupled LLM provider abstraction, versioned Jinja2 prompt templates, deterministic verification engine, and interactive Prompt Studio UI.
* **Key Integrations:**
  - `BaseLLMProvider` interface supporting offline local deterministic generation (`LocalDeterministicLLMProvider`) alongside live OpenAI and Gemini cloud connectors.
  - Three-stage chained prompt pipeline with stored Jinja2 versioning:
    - `prompt1_factual_v1.jinja2` vs `prompt1_factual_v2.jinja2`: Unconstrained prose vs. structured `[METRIC:metric_id]` factual claims.
    - `prompt2_insights_v1.jinja2` vs `prompt2_insights_v2.jinja2`: Ungrounded speculation vs. explicit `[HYPOTHESIS]` tagging and mandatory refusal (`"Insufficient data"`).
    - `prompt3_report_v1.jinja2` vs `prompt3_report_v2.jinja2`: Conversational markdown vs. strict Pydantic `ExecutiveCommercialReport` JSON.
  - `VerificationEngine`: Deterministic regex verification auditing cited figures within a 0.5% tolerance window against Pandas ground truth.
  - Automated evaluation harness ([evaluate_prompts.py](file:///d:/Insightforge/backend/scripts/evaluate_prompts.py)) testing 4 golden commercial scenarios.
* **Empirical Results:** Prompt v2 achieved 100.0% numerical accuracy (vs. 33.3% on v1) and 100.0% schema pass rate (vs. 0.0% on v1).
* **Test Milestone:** Backend suite expanded to 57 passing tests.

---

### Phase 3: Machine Learning Intelligence (Stage 6)
* **Scope:** Time-series sales forecasting and unsupervised transaction anomaly detection.
* **Key Integrations:**
  - **XGBoost Sales Forecaster:** Forward-shifted lag features (1..4) and rolling statistics (3/6 periods) preventing future target leakage. Strict chronological 80/20 holdout split.
  - **Empirical Baseline Discipline:** Evaluated against a Seasonal Naive lag-1 persistence model. The system demonstrated academic honesty by disclosing when the baseline was competitive rather than fabricating superior ML metrics.
  - **Isolation Forest Outlier Detector:** Feature engineering on SKU-relative price and volume deviations, off-hours transaction flags, and cancellation status. Output continuous $[0, 1]$ anomaly scores with 4 explainable pattern tags (`EXTREME_UNIT_PRICE`, `UNUSUAL_BULK_QUANTITY`, `CANCELLATION_SPIKE`, `OFF_HOURS_ACTIVITY`).
  - Legal disclaimers distinguishing statistical outliers from confirmed fraud.
* **Test Milestone:** Backend suite expanded to 73 passing tests; 100% recall on synthetic outlier injection tests.

---

### Phase 4: Business Knowledge Base & Hybrid RAG Retrieval (Stage 7)
* **Scope:** Ingestion of unstructured commercial documents, vector embeddings, and contextual grounding.
* **Key Integrations:**
  - Multi-format ingestion supporting PDF (page-indexed via `pypdf`) and TXT documents.
  - Sliding-window word-level chunking (400 words, 60-word overlap) preserving source provenance (`Page X, chunk Y`).
  - Ingestion sanitization: Neutralizes indirect prompt injections (e.g., `IGNORE PREVIOUS INSTRUCTIONS`) at ingestion time.
  - Dense vector embeddings with `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) and in-memory cosine similarity retrieval with a 0.25 similarity floor.
  - Contextual injection into Prompt Stage 2 without mathematical contamination.
* **Test Milestone:** Backend suite expanded to 88 passing tests.

---

### Phase 5: Controlled LangGraph AI Business Analyst (Stage 8)
* **Scope:** Stateful conversational AI copilot executing strictly approved business tools within safe graph boundaries.
* **Key Integrations:**
  - LangGraph 4-node directed graph: `classify_and_plan` $\rightarrow$ `validate_arguments` $\rightarrow$ `execute_tools` $\rightarrow$ `synthesize_response`.
  - 7 Approved Business Analysis Tools: `get_business_kpis`, `analyze_revenue_trends`, `get_product_performance`, `forecast_sales`, `detect_anomalies`, `retrieve_business_documents`, `generate_executive_report`.
  - Security Guardrails: Zero arbitrary code execution (`eval`/`exec`), zero raw SQL generation, parameter bounds clamping, prompt injection defense, and out-of-domain safe fallbacks.
  - Interactive AI Copilot UI with collapsible tool execution trace drawer, inline interactive Recharts visualizations, and evidence citation tags.
* **Test Milestone:** Backend suite expanded to 101 passing tests; commit `0085a4b`.

---

### Phase 6: Boardroom Executive PDF Reports & Academic Delivery (Stage 9)
* **Scope:** Vector-rendered multi-page PDF generation, PWA capabilities, full lifecycle integration testing, and 12-benchmark academic research evaluation.
* **Key Integrations:**
  - ReportLab PDF engine with custom `NumberedCanvas` (`Page X of Y`), corporate running headers, 8 structured audit sections, and 3 embedded high-DPI Matplotlib figures.
  - Progressive Web App (PWA) manifest and Service Worker (`sw.js`) with static bundle caching and `/api/` network-only bypass.
  - Full lifecycle integration test ([test_e2e_journey.py](file:///d:/Insightforge/backend/app/tests/test_e2e_journey.py)) verifying registration through PDF generation.
  - Automated 12-benchmark academic research evaluation script ([run_academic_evaluation.py](file:///d:/Insightforge/backend/scripts/run_academic_evaluation.py)) exporting [academic_research_evaluation.json](file:///d:/Insightforge/data/samples/academic_research_evaluation.json).
* **Test Milestone:** 110 passed backend Pytest tests, 10 passed Vitest tests; commit `a281960`.

---

### Phase 7: Indian Business Edition & Localization (Master Prompt 7)
* **Scope:** Transform the platform into an authentic, credible Indian commercial product for wholesale distributors, FMCG retailers, and college demonstrations.
* **Key Integrations:**
  - **Dataset Research:** Authoritative survey of public Indian datasets across data.gov.in (AGMARKNET Mandi prices) and Kaggle (Amazon India Seller Central, Retail FMCG).
  - **BharatTrade Distributors FMCG Simulation:** High-fidelity deterministic seeded simulation (6,000 records) representing a Pune-headquartered distributor with regional hubs across Maharashtra, Karnataka, Telangana, Delhi NCR, Gujarat, Tamil Nadu, and Rajasthan. Explicit unit costs (COGS), pack pricing, and GST tax slabs (5%, 12%, 18%).
  - **Real Mandi Data Script:** Automated ingestion script ([ingest_indian_mandi_data.py](file:///d:/Insightforge/backend/scripts/ingest_indian_mandi_data.py)) connecting to official data.gov.in APMC feeds.
  - **Centralized INR Formatting:** Centralized Indian locale formatting (`frontend/src/lib/utils.ts` and `analytics_service.py`), supporting standard Indian comma separation (`₹1,25,000`), compact Lakhs/Crores notations (`₹12.50 Lakh`, `₹1.25 Cr`), and DD/MM/YYYY dates.
  - **Localized RAG Knowledge Base:** Added realistic Indian distributor policies (BharatTrade Pricing Policy, Return Policy, Regional Sales Targets).
  - **Localized PDF Reports & Copilot:** Executive PDF engine branded for BharatTrade Distributors with INR currency, GST disclosures, and Indian commercial example queries.

---

## 3. Critical Technical Challenges Encountered & Fixes

1. **Passlib Bcrypt Deprecation on Python 3.12/3.14:**
   - *Problem:* `passlib.context.CryptContext` threw `AttributeError: module 'bcrypt' has no attribute '__about__'` due to changes in modern `bcrypt >= 4.1.0`.
   - *Fix:* Replaced `passlib` with direct native `bcrypt` calls (`bcrypt.hashpw` and `bcrypt.checkpw`) with explicit 72-byte truncation boundaries in `backend/app/core/security.py`.
2. **Future Target Leakage in Time-Series Feature Engineering:**
   - *Problem:* Naive rolling window aggregations accidentally exposed future target values $y_t$ during feature calculation.
   - *Fix:* Strictly enforced forward-shifting (`.shift(1)`) on all lag and rolling window features prior to model ingestion; enforced chronological 80/20 train/test holdouts.
3. **Indirect Prompt Injection in Knowledge Base Uploads:**
   - *Problem:* Adversarial instructions embedded in uploaded invoices or contracts could hijack downstream LLM reasoning.
   - *Fix:* Implemented regex sanitization during document extraction in `retrieval_service.py` to neutralize adversarial prompt patterns before chunking and dense vector embedding.
4. **Vite TypeScript Environment Missing Property Error:**
   - *Problem:* `src/main.tsx` failed compilation on `import.meta.env` with `error TS2339: Property 'env' does not exist on type 'ImportMeta'`.
   - *Fix:* Created `frontend/src/vite-env.d.ts` with `/// <reference types="vite/client" />`, enabling standard Vite typing.
5. **Formatting Null & Sign Regressions in `utils.ts`:**
   - *Problem:* Remote commit `871be7a` introduced non-null-safe currency and percentage formatters, failing 2 Vitest unit tests.
   - *Fix:* Overhauled `frontend/src/lib/utils.ts` with full null/undefined safety, explicit percentage signs (`+12.5%`, `-5.3%`), and first-class Indian Rupee (INR / `₹`) formatting with Lakh and Crore support.

---

## 4. Current Status & Production Readiness

* **Backend Tests:** **110 passing Pytest tests** (100% pass rate).
* **Frontend Tests:** **13 passing Vitest tests** (100% pass rate).
* **Frontend Production Build:** Clean Vite production build (`dist/`) generated with zero type errors.
* **Remote Git Sync:** Fully synchronized with `origin/main` at commit `74266dc`.
* **Security & Governance:** Zero committed secrets or API keys; strict multi-tenant data isolation; complete separation between statistical outliers and verified fraud.
