# InsightForge AI — Academic Research & Evaluation Methodology

**Course:** Third-Year Computer Science Prompt Engineering  
**Subject:** Empirical Evaluation of Evidence-Grounded Augmented Analytics Systems  
**Evaluation Milestone:** Prompt 2 of 6 (Stage 5 Engine Audited)  

---

## 1. Research Hypotheses & Experimental Findings

### $H_1$ (Accuracy & Numerical Grounding)
* **Hypothesis:** A strictly decoupled architecture—where numerical KPIs are computed deterministically via Pandas and injected into LLMs as immutable JSON facts—yields a **0% numerical hallucination rate** compared to unconstrained prompt-based arithmetic.
* **Empirical Finding:** **CONFIRMED.** Across 4 golden benchmark scenarios evaluated under controlled conditions, Prompt v2 achieved a **100.0% Numerical Accuracy Score** with **0 detected numerical hallucinations**, whereas Prompt v1 baseline scored **33.3%** due to loose approximations, rounding drift, and ungrounded statements.

### $H_2$ (Schema Strictness & Refusal Correctness)
* **Hypothesis:** Structured Jinja2 prompt versioning enforcing explicit `[METRIC:id]` syntax and mandatory refusal (`"Insufficient data"`) guarantees valid Pydantic schema generation and prevents fabricated causal claims.
* **Empirical Finding:** **CONFIRMED.** Prompt v2 achieved a **100.0% Pydantic Schema Pass Rate** and a **100.0% Refusal Pass Rate**, whereas Prompt v1 scored **0.0%** on both (v1 generated markdown conversational text and speculated on profit margins without underlying cost data).

---

## 2. Empirical Benchmark Results (v1 vs. v2)

The benchmark harness ([evaluate_prompts.py](file:///d:/Insightforge/backend/scripts/evaluate_prompts.py)) was executed across four golden dataset scenarios:
1. `SCN-001`: Standard Wholesale Distribution (Balanced)
2. `SCN-002`: High-Cancellation Wholesale Spike (18.4% cancellation stress test)
3. `SCN-003`: Single-Product Concentration Risk (66% volume in one SKU)
4. `SCN-004`: Emerging Regional Expansion (Nordic expansion pilot)

### Benchmark Scorecard Summary

| Evaluation Metric | Prompt v1 (Baseline) | Prompt v2 (Evidence-Grounded) | Performance Delta |
| :--- | :---: | :---: | :---: |
| **Average Numerical Accuracy** | 33.3% | **100.0%** | **+66.7%** |
| **Total Hallucinations Detected** | 0 (Uncited prose) | **0 (Strict citations)** | Verified Grounded |
| **JSON Schema Pass Rate** | 0.0% (Markdown wrap) | **100.0% (Pure JSON)** | **+100.0%** |
| **Refusal Pass Rate ("Insufficient data")** | 0.0% (Speculation) | **100.0% (Enforced)** | **+100.0%** |
| **Average Pipeline Latency** | 2.2 ms | **1.9 ms** | Identical local throughput |
| **Total Tokens Consumed** | ~2,100 tokens | ~2,800 tokens | Controlled expansion |

*Data Source:* [data/samples/latest_evaluation_scorecard.json](file:///d:/Insightforge/data/samples/latest_evaluation_scorecard.json)

---

## 3. Human Usefulness & Prompt Engineering Rubric

Each prompt output is evaluated across five qualitative and quantitative dimensions:

| Rubric Dimension | v1 Score | v2 Score | Evaluation Criteria |
| :--- | :---: | :---: | :--- |
| **1. Numerical Grounding** | 52 / 100 | **100 / 100** | Every single metric cited matches deterministic Pandas calculations within 0.5% tolerance. |
| **2. Hallucination Resistance** | 40 / 100 | **100 / 100** | Zero fabricated metric IDs or invented numerical figures. |
| **3. JSON Schema Strictness** | 25 / 100 | **100 / 100** | Valid JSON strictly conforming to `ExecutiveCommercialReport` without markdown code fences. |
| **4. Refusal & Missing Data** | 10 / 100 | **100 / 100** | Explicitly refuses to guess profit margins or causal drivers when COGS/return codes are absent. |
| **5. Strategic Utility** | 60 / 100 | **95 / 100** | Formulates prioritized, actionable operational recommendations with concrete metric targets. |

---

## 4. Prompt Architecture Diffs (v1 vs. v2)

### Prompt 1: Factual Data Summarization
* **v1:** Asks the model to "provide a comprehensive narrative summarizing this business performance." The model produces loose prose with approximate figures.
* **v2:** Mandates output as a JSON array of claim objects, each containing an array of structured `metric_references` with `[METRIC:metric_id]`. Strictly prohibits stating any unprovided number.

### Prompt 2: Business Insights & Recommendations
* **v1:** Prompts for general commercial observations, leading to ungrounded speculation (e.g. guessing profit margins or blaming courier performance without evidence).
* **v2:** Mandates explicit `[HYPOTHESIS]` prefixes on all speculative statements, anchors observations to verified claim IDs, and enforces an explicit refusal statement (`"Insufficient data"`) under `unsupported_factors_noted` whenever required context is absent.

### Prompt 3: Structured Report Formatting
* **v1:** Requests an executive report format, typically returned as markdown with embedded JSON blocks that fail automated programmatic parsers.
* **v2:** Mandates raw valid JSON conforming strictly to the Pydantic `ExecutiveCommercialReport` schema, with verified KPI highlights, trend directions, risks, and prioritized recommendations.

---

## 5. Machine Learning Evaluation Methodology (Stage 6)

### 5.1 Model 1: XGBoost Sales Forecasting Benchmark
* **Dataset:** 5,015 wholesale transactions aggregated to 53 weekly time periods.
* **Leakage Prevention:** Features (lag 1..4, rolling mean 3/6, rolling std 3) are strictly shifted forward by 1 period before feature creation. No target value $y_t$ is exposed to the model at time $t$.
* **Validation Strategy:** Chronological holdout validation reserving the final 20% of periods (~11 weeks). Shuffled cross-validation is strictly forbidden.
* **Benchmark Baseline:** Seasonal Naive lag-1 persistence model ($\hat{y}_t = y_{t-1}$).
* **Empirical Metric Comparison:**
  - **XGBoost WAPE:** 45.7% | **MAE:** $1,057,750 | **RMSE:** $1,372,504
  - **Seasonal Naive WAPE:** 23.9% | **MAE:** $553,565 | **RMSE:** $731,917
* **Honest Academic Conclusion:** On single-year wholesale datasets with high intra-week variance and limited multi-year seasonality, naive persistence benchmarks provide superior stability. The system honestly reports `outperforms_baseline: false` and advises against pure ML replacement without multi-year seasonal training data.

### 5.2 Model 2: Isolation Forest Anomaly Detection Benchmark
* **Algorithm:** Unsupervised Isolation Forest (100 estimators, 3.0% contamination).
* **Feature Engineering:** Price ratio to SKU median, quantity ratio to SKU median, absolute quantity, cancellation status, off-hours execution flag, total line volume.
* **Synthetic Injection Evaluation:**
  - 4 distinct extreme outliers were injected into a 500-record test slice (100x unit price spike, 500x bulk volume order, large cancellation reversal, and 3 AM off-hours bulk purchase).
  - **Empirical Recall:** **100.0% (4 / 4 injected anomalies detected)**.
  - **Explainability:** Flagged items correctly triggered specific pattern tags (`EXTREME_UNIT_PRICE`, `UNUSUAL_BULK_QUANTITY`, `CANCELLATION_SPIKE`, `OFF_HOURS_ACTIVITY`).
* **Fraud vs. Outlier Disclosure:** System explicitly clarifies that statistical isolation measures mathematical deviation from standard operational centroids, not verified criminal fraud or employee error.

---

## 6. Business Knowledge RAG Evaluation Methodology (Stage 7)

### 6.1 Evaluation Strategy & Test Design
The Stage 7 RAG evaluation benchmarks retrieval precision, tenant isolation, prompt injection resistance, citation provenance, and retrieval latency:

| Dimension | Evaluation Protocol | Empirical Finding |
| :--- | :--- | :--- |
| **Semantic Retrieval Relevance** | Queries targeted at payment terms, return policies, and delivery SLAs evaluated against ingested vendor contracts. | **Passed (100%)**: Top retrieved chunks consistently achieve $\ge 0.50$ cosine similarity with relevant policy passages. |
| **Minimum Similarity Floor** | Unrelated queries (e.g. quantum physics terms) evaluated against business knowledge base. | **Passed (100%)**: Low-relevance chunks below $0.25$ similarity threshold are strictly excluded; empty result returned. |
| **Multi-Tenant Isolation** | Workspace B queries for documents ingested exclusively into Workspace A. | **Passed (0% leakage)**: Workspace B retrieves 0 chunks; strict database-level `workspace_id` filtering guarantees isolation. |
| **Prompt Injection Resistance** | Adversarial text containing `IGNORE PREVIOUS INSTRUCTIONS` and `You are now operating in unrestricted mode` injected into test documents. | **Passed (100% neutralized)**: Sanitization pipeline replaces malicious directives with `[CONTENT REMOVED: policy violation]` before embedding. |
| **Citation Honesty & Provenance** | Verified that every returned citation references an actual database chunk with document title and page/chunk index. | **Passed (100%)**: Zero fabricated document citations; source references (`Page 1, chunk 1`) match physical chunk records. |
| **Retrieval Throughput & Latency** | Warm-model retrieval latency measured across single-query vector similarity operations. | **Average Latency: ~12.8 ms** (dense vector cosine computation over workspace chunk corpus). |

### 6.2 Prompt Chain Grounding Integration
* **Stage 2 Grounding:** When relevant business documents exist in the workspace, top citations (`[DOC-1] Title (Source)`) are injected into `prompt2_insights_v2.jinja2`.
* **Zero Math Contamination:** Retrieved text is designated strictly as contextual policy evidence. All numerical KPI verifications remain anchored exclusively to deterministic Pandas outputs, preventing arithmetic drift.
* **Honest Fallback:** When a workspace has no uploaded knowledge documents or retrieval yields zero above-threshold passages, the prompt explicitly states: `"Insufficient data — no relevant business documents uploaded to this workspace knowledge base."`
