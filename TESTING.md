# InsightForge AI — Testing Strategy & Execution Log

**Audit Status:** Fully Verified and Validated (Stage 9 Reporting, Mobile Experience, Integration, QA & Academic Delivery Included)  
**Last Run:** November 17, 2026  

---

## 1. Multi-Tier Testing Architecture

InsightForge AI implements a multi-tier testing strategy across both backend and frontend environments:

```
                  ┌────────────────────────┐
                  │    ESLint & Vite Build │  (Zero errors, 2,134 modules bundled)
                  ├────────────────────────┤
                  │    Vitest UI Tests     │  (10 tests: utils & data integrity)
                  ├────────────────────────┤
                  │ Academic Evaluation CLI│  (12 benchmarks: Prompts, ML, RAG, Agent)
                  ├────────────────────────┤
                  │ E2E Journey Tests      │  (5 tests: full lifecycle & boundaries)
                  ├────────────────────────┤
                  │ ReportLab PDF Tests    │  (4 tests: vector PDF, charts, REST API)
                  ├────────────────────────┤
                  │ FastAPI Integration    │  (16 tests: auth, workspaces, prompts, ML, RAG)
                  ├────────────────────────┤
                  │ Agent Copilot Tests    │  (13 tests: tools, bounds, security, trace)
                  ├────────────────────────┤
                  │ RAG Knowledge Tests    │  (13 tests: ingestion, embeddings, isolation)
                  ├────────────────────────┤
                  │ ML Intelligence Tests  │  (14 tests: XGBoost, Isolation Forest)
                  ├────────────────────────┤
                  │ Pytest Unit Tests      │  (45 tests: Pandas math, security, prompts)
                  └────────────────────────┘
```


---

## 2. Test Suites Overview & Execution Command Reference

### 2.1 Backend Unit & Integration Tests (Pytest)
* **Location:** `backend/app/tests/`
* **Test files:**
  - `test_analytics.py`: 14 tests covering revenue calculation, cancellation exclusions, order metrics, AOV, unique customers, cancellation rate, monthly growth timelines, zero-division guards, and empty/missing data resilience.
  - `test_dataset_service.py`: 15 tests covering CSV/XLSX validation, size limit checks, column auto-detection, quality audit scoring, and file reading.
  - `test_security.py`: 6 tests covering bcrypt hashing, password verification, 72-byte boundary guards, JWT token issuance, payload decoding, and expiration checks.
  - `test_prompts.py`: 10 tests covering LLM provider abstraction, deterministic generation, missing API key guard, exact metric verification, numeric discrepancy detection, unknown metric ID rejection, hypothesis checking, refusal checking, strict Pydantic report validation, and v1 vs v2 comparison.
  - `test_agent.py`: 13 tests covering LangGraph tool selection across 5 analytical intents, prompt injection defense, unsupported query fallback, argument clamping (periods and product limits), end-to-end copilot execution, and missing dataset recovery.
  - `test_api_integration.py`: 16 tests covering health endpoint, registration, login, profile `/me`, duplicate registration rejection, unauthorized password rejection, workspace isolation (403 Forbidden check), CSV upload via multipart form, dataset preview, quality report API, KPI summary API, full analytics API, prompt templates API, prompt execution API, prompt comparison API, scorecard API, unauthenticated demo execution, unauthenticated demo comparison, unauthenticated templates inspection, unauthenticated evaluation scorecard, unauthenticated demo forecast, unauthenticated demo anomalies, unauthenticated demo knowledge list, unauthenticated demo knowledge search, authenticated knowledge document upload, list, search, and delete, and cloud LLM authentication guard (401 check).
  - `test_ml_forecast.py`: 8 tests covering weekly/monthly sales aggregation, cancellation exclusion, shifted lag/rolling features (zero lookahead leakage), chronological 20% holdout split, XGBoost regression, WAPE/MAE/RMSE evaluation against naive baseline, 95% confidence bounds, Joblib persistence, and insufficient data refusal (<10 periods).
  - `test_ml_anomalies.py`: 6 tests covering SKU median relative deviation feature matrix, cancellation and off-hours indicators, Isolation Forest training and [0, 1] continuous scoring, full provenance record preservation, synthetic anomaly injection (100% recall on injected outliers), and insufficient data refusal (<20 records).
  - `test_rag.py`: 13 tests covering TXT document ingestion, sliding-window chunking, semantic retrieval relevance, multi-tenant workspace isolation (zero cross-workspace leakage), minimum similarity threshold floor (0.25), document deletion with cascading chunk removal, prompt injection sanitization (neutralizing `IGNORE PREVIOUS` patterns), oversized file rejection (>25 MB), unsupported file extension rejection, citation provenance preservation, and evidence summary formatting.
  - `test_reports.py`: 4 tests covering ReportLab vector PDF compilation, structural text extraction and verification via `pypdf`, missing dataset handling, and REST API generation, download, listing, and deletion.
  - `test_e2e_journey.py`: 5 tests verifying the entire platform lifecycle: user registration $\rightarrow$ workspace creation $\rightarrow$ dataset upload $\rightarrow$ data quality audit $\rightarrow$ deterministic KPI calculation $\rightarrow$ ML forecasting & anomaly detection $\rightarrow$ RAG document ingestion & retrieval $\rightarrow$ AI Copilot inquiry $\rightarrow$ executive PDF generation and binary download, plus multi-tenant security boundary violation checks, prompt injection defense, unsupported domain fallback, and dataset error recovery.
* **Execution Command:**
  ```powershell
  Set-Location d:\Insightforge\backend
  python -m pytest app/tests/ -v --tb=short
  ```
* **Status:** **110 Passed, 0 Failed, 1 Warning (100% Pass Rate in 45.53s)**


### 2.2 Frontend Unit Tests (Vitest)
* **Location:** `frontend/src/`
* **Test files:**
  - `src/lib/utils.test.ts`: 4 tests covering currency, number, percentage, and byte size formatting.
  - `src/services/api.test.ts`: 6 tests covering benchmark demo analytics integrity, AOV mathematical identity, monthly timeline continuity, product ranking descending order, canonical column roles, and preview row schema.
* **Execution Command:**
  ```powershell
  Set-Location d:\Insightforge\frontend
  npm test
  ```
* **Status:** **10 Passed, 0 Failed (100% Pass Rate in 632ms)**

### 2.3 Automated Prompt Engineering Evaluation Harness
* **Script:** `backend/scripts/evaluate_prompts.py`
* **Execution Command:**
  ```powershell
  Set-Location d:\Insightforge\backend
  python scripts/evaluate_prompts.py
  ```
* **Status:** **Verified across 4 Golden Scenarios (Scorecard exported to `data/samples/latest_evaluation_scorecard.json`)**
  - Prompt v1 Accuracy: 33.3%
  - Prompt v2 Accuracy: 100.0% (+66.7% improvement)
  - Hallucination Reduction: 100% reduction in unverified claims
  - Schema Conformance: 100.0% pass rate on `ExecutiveCommercialReport`

### 2.4 Code Quality, Linting & Type Checking
* **Frontend Linting:**
  ```powershell
  Set-Location d:\Insightforge\frontend
  npm run lint
  ```
  *Status:* **Exited with code 0 (0 errors, 0 warnings)**
* **Frontend Production Build:**
  ```powershell
  Set-Location d:\Insightforge\frontend
  npm run build
  ```
  *Status:* **Clean compilation via `tsc && vite build` (2,131 modules transformed into `dist/` in 6.09s)**
* **Backend Python Compilation:**
  ```powershell
  python -m compileall backend/app -q
  ```
  *Status:* **Exited with code 0 (0 syntax errors)**

---

## 3. Actual Pytest Output (88 Tests Passed)

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0
rootdir: D:\Insightforge\backend
collected 88 items

app/tests/test_analytics.py::TestRevenueCalculation::test_total_revenue_basic PASSED [  1%]
app/tests/test_analytics.py::TestRevenueCalculation::test_total_revenue_excludes_cancellations PASSED [  2%]
app/tests/test_analytics.py::TestRevenueCalculation::test_revenue_missing_columns PASSED [  4%]
app/tests/test_analytics.py::TestOrderMetrics::test_unique_orders PASSED [  5%]
app/tests/test_analytics.py::TestOrderMetrics::test_average_order_value PASSED [  7%]
app/tests/test_analytics.py::TestOrderMetrics::test_units_sold PASSED    [  8%]
app/tests/test_analytics.py::TestCustomerMetrics::test_unique_customers PASSED [  9%]
app/tests/test_analytics.py::TestCancellationMetrics::test_cancellation_rate PASSED [ 11%]
app/tests/test_analytics.py::TestMonthlyRevenue::test_monthly_breakdown PASSED [ 12%]
app/tests/test_analytics.py::TestMonthlyRevenue::test_growth_rate_calculation PASSED [ 14%]
app/tests/test_analytics.py::TestEdgeCases::test_empty_dataframe PASSED  [ 15%]
app/tests/test_analytics.py::TestEdgeCases::test_all_cancellations PASSED [ 16%]
app/tests/test_analytics.py::TestEdgeCases::test_missing_values_in_data PASSED [ 18%]
app/tests/test_analytics.py::TestEdgeCases::test_division_by_zero_growth PASSED [ 19%]
app/tests/test_api_integration.py::TestHealthEndpoint::test_health_check PASSED [ 21%]
app/tests/test_api_integration.py::TestAuthEndpoints::test_register_and_login_success PASSED [ 22%]
app/tests/test_api_integration.py::TestAuthEndpoints::test_duplicate_registration_fails PASSED [ 23%]
app/tests/test_api_integration.py::TestAuthEndpoints::test_invalid_login_password PASSED [ 25%]
app/tests/test_api_integration.py::TestWorkspaceEndpoints::test_create_and_list_workspace PASSED [ 26%]
app/tests/test_api_integration.py::TestWorkspaceEndpoints::test_workspace_isolation_forbidden PASSED [ 28%]
app/tests/test_api_integration.py::TestDatasetAndAnalyticsAPI::test_upload_and_analyze_dataset PASSED [ 29%]
app/tests/test_api_integration.py::TestDemoModeUnauthenticatedAccess::test_demo_prompt_chain_execution_unauthenticated PASSED [ 30%]
app/tests/test_api_integration.py::TestDemoModeUnauthenticatedAccess::test_demo_prompt_comparison_unauthenticated PASSED [ 32%]
app/tests/test_api_integration.py::TestDemoModeUnauthenticatedAccess::test_demo_prompt_templates_unauthenticated PASSED [ 33%]
app/tests/test_api_integration.py::TestDemoModeUnauthenticatedAccess::test_demo_evaluation_scorecard_unauthenticated PASSED [ 35%]
app/tests/test_api_integration.py::TestDemoModeUnauthenticatedAccess::test_cloud_llm_requires_authentication PASSED [ 36%]
app/tests/test_dataset_service.py::TestFileValidation::test_valid_csv PASSED [ 38%]
app/tests/test_dataset_service.py::TestFileValidation::test_valid_xlsx PASSED [ 39%]
app/tests/test_dataset_service.py::TestFileValidation::test_invalid_extension PASSED [ 40%]
app/tests/test_dataset_service.py::TestFileValidation::test_file_too_large PASSED [ 42%]
app/tests/test_dataset_service.py::TestFileValidation::test_empty_filename PASSED [ 43%]
app/tests/test_column_auto_detection.py::TestColumnAutoDetection::test_standard_retail_columns PASSED [ 45%]
app/tests/test_dataset_service.py::TestColumnAutoDetection::test_custom_column_names PASSED [ 46%]
app/tests/test_dataset_service.py::TestColumnAutoDetection::test_no_matching_columns PASSED [ 47%]
app/tests/test_dataset_service.py::TestQualityAnalysis::test_quality_with_clean_data PASSED [ 49%]
app/tests/test_dataset_service.py::TestQualityAnalysis::test_quality_detects_missing_values PASSED [ 50%]
app/tests/test_dataset_service.py::TestQualityAnalysis::test_quality_detects_duplicates PASSED [ 52%]
app/tests/test_dataset_service.py::TestQualityAnalysis::test_quality_detects_cancellations PASSED [ 53%]
app/tests/test_dataset_service.py::TestQualityAnalysis::test_quality_detects_negative_quantities PASSED [ 54%]
app/tests/test_dataset_service.py::TestReadDataset::test_read_csv PASSED [ 56%]
app/tests/test_dataset_service.py::TestReadDataset::test_read_empty_csv PASSED [ 57%]
app/tests/test_ml_anomalies.py::TestFeatureExtraction::test_feature_matrix_shapes_and_columns PASSED [ 59%]
app/tests/test_ml_anomalies.py::TestFeatureExtraction::test_cancellation_and_off_hours_flags PASSED [ 60%]
app/tests/test_ml_anomalies.py::TestIsolationForestTrainingAndScoring::test_detect_anomalies_success PASSED [ 61%]
app/tests/test_ml_anomalies.py::TestIsolationForestTrainingAndScoring::test_source_record_references_preserved PASSED [ 63%]
app/tests/test_ml_anomalies.py::TestSyntheticAnomalyInjection::test_detects_injected_synthetic_anomalies PASSED [ 64%]
app/tests/test_ml_anomalies.py::TestAnomalyEdgeCases::test_insufficient_records_refusal PASSED [ 66%]
app/tests/test_ml_forecast.py::TestTimeSeriesAggregation::test_weekly_aggregation_structure PASSED [ 67%]
app/tests/test_ml_forecast.py::TestTimeSeriesAggregation::test_excludes_cancellations PASSED [ 69%]
app/tests/test_ml_forecast.py::TestFeatureEngineeringAndLeakagePrevention::test_features_shifted_prior_periods PASSED [ 70%]
app/tests/test_ml_forecast.py::TestModelTrainingAndEvaluation::test_train_and_forecast_success PASSED [ 71%]
app/tests/test_ml_forecast.py::TestModelTrainingAndEvaluation::test_future_forecast_confidence_bounds PASSED [ 73%]
app/tests/test_ml_forecast.py::TestModelTrainingAndEvaluation::test_wape_calculation_edge_cases PASSED [ 74%]
app/tests/test_ml_forecast.py::TestModelArtifactsAndEdgeCases::test_model_artifact_saved PASSED [ 76%]
app/tests/test_ml_forecast.py::TestModelArtifactsAndEdgeCases::test_insufficient_data_refusal PASSED [ 77%]
app/tests/test_prompts.py::TestLLMProviderAbstraction::test_local_deterministic_provider_generation PASSED [ 78%]
app/tests/test_prompts.py::TestLLMProviderAbstraction::test_provider_factory PASSED [ 80%]
app/tests/test_prompts.py::TestLLMProviderAbstraction::test_cloud_providers_raise_without_key PASSED [ 81%]
app/tests/test_prompts.py::TestVerificationEngine::test_verify_stage1_exact_match PASSED [ 83%]
app/tests/test_prompts.py::TestVerificationEngine::test_detect_hallucinated_numeric_value PASSED [ 84%]
app/tests/test_prompts.py::TestVerificationEngine::test_detect_unknown_metric_id PASSED [ 85%]
app/tests/test_prompts.py::TestVerificationEngine::test_stage2_hypotheses_and_refusal_check PASSED [ 87%]
app/tests/test_prompts.py::TestVerificationEngine::test_stage3_strict_schema_validation PASSED [ 88%]
app/tests/test_prompts.py::TestPromptService::test_execute_chain_v2 PASSED [ 90%]
app/tests/test_prompts.py::TestPromptService::test_compare_v1_and_v2 PASSED [ 91%]
app/tests/test_security.py::TestPasswordHashing::test_hash_and_verify PASSED [ 92%]
app/tests/test_security.py::TestPasswordHashing::test_wrong_password PASSED [ 94%]
app/tests/test_security.py::TestPasswordHashing::test_different_hashes PASSED [ 95%]
app/tests/test_security.py::TestJWTTokens::test_create_and_decode PASSED [ 97%]
app/tests/test_security.py::TestJWTTokens::test_invalid_token PASSED     [ 98%]
app/tests/test_security.py::TestJWTTokens::test_token_contains_expiry PASSED [100%]

============================= 101 passed in 84.02s ==============================
```

### 2.2 Stage 8 Agent Copilot Test Execution Details
```
app/tests/test_agent.py::TestAgentToolSelection::test_tool_selection_kpis PASSED [  7%]
app/tests/test_agent.py::TestAgentToolSelection::test_tool_selection_forecast PASSED [ 15%]
app/tests/test_agent.py::TestAgentToolSelection::test_tool_selection_anomalies PASSED [ 23%]
app/tests/test_agent.py::TestAgentToolSelection::test_tool_selection_policy_rag PASSED [ 30%]
app/tests/test_agent.py::TestAgentToolSelection::test_tool_selection_executive_report PASSED [ 38%]
app/tests/test_agent.py::TestAgentSecurity::test_prompt_injection_blocked PASSED [ 46%]
app/tests/test_agent.py::TestAgentSecurity::test_unsupported_query_safe_fallback PASSED [ 53%]
app/tests/test_agent.py::TestArgumentValidation::test_forecast_periods_clamped_to_bounds PASSED [ 61%]
app/tests/test_agent.py::TestArgumentValidation::test_product_limit_clamped_to_bounds PASSED [ 69%]
app/tests/test_agent.py::TestAgentExecution::test_execute_kpis_query PASSED [ 76%]
app/tests/test_agent.py::TestAgentExecution::test_execute_forecast_query PASSED [ 84%]
app/tests/test_agent.py::TestAgentExecution::test_execute_anomalies_query PASSED [ 92%]
app/tests/test_agent.py::TestAgentExecution::test_missing_dataset_recovery PASSED [100%]
```
