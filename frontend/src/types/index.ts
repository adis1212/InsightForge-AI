export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface WorkspaceMember {
  id: string
  user_id: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  user_email: string
  user_name: string
}

export interface Workspace {
  id: string
  name: string
  description?: string | null
  created_at: string
  member_count: number
  user_role: string
  members?: WorkspaceMember[]
}

export interface DatasetColumn {
  id: string
  name: string
  dtype: string
  mapped_role?: string | null
  null_count: number
  unique_count: number
  sample_values?: any[] | null
}

export interface QualityReport {
  dataset_id: string
  total_rows: number
  total_columns: number
  missing_values: Record<string, number>
  missing_percentages: Record<string, number>
  duplicate_rows: number
  duplicate_percentage: number
  date_issues: number
  negative_quantities: number
  zero_prices: number
  cancellation_count: number
  data_quality_score: number
}

export interface Dataset {
  id: string
  workspace_id: string
  name: string
  original_filename: string
  file_size: number
  file_type: string
  row_count?: number | null
  column_count?: number | null
  status: 'uploaded' | 'processing' | 'ready' | 'error'
  upload_error?: string | null
  quality_report?: QualityReport | null
  column_mapping?: Record<string, string> | null
  created_at: string
  columns?: DatasetColumn[]
}

export interface DatasetPreview {
  dataset_id: string
  columns: string[]
  rows: Record<string, any>[]
  total_rows: number
}

export interface KPIValue {
  name: string
  value?: number | null
  formatted: string
  description: string
  available: boolean
  unavailable_reason?: string | null
}

export interface KPISummary {
  dataset_id: string
  total_revenue: KPIValue
  unique_orders: KPIValue
  units_sold: KPIValue
  average_order_value: KPIValue
  unique_customers: KPIValue
  cancellation_rate: KPIValue
}

export interface RevenueGrowth {
  period: string
  revenue: number
  growth_rate?: number | null
}

export interface ProductRanking {
  rank: number
  stock_code: string
  description: string
  total_revenue: number
  units_sold: number
}

export interface GeographicPerformance {
  country: string
  revenue: number
  order_count: number
  customer_count: number
}

export interface AnalyticsResponse {
  dataset_id: string
  summary: KPISummary
  monthly_revenue: RevenueGrowth[]
  top_products: ProductRanking[]
  geographic_performance: GeographicPerformance[]
  cancellation_stats?: Record<string, any> | null
}

// Prompt Engineering Types
export interface MetricReference {
  metric_id: string
  cited_value: number
  formatted_value?: string | null
  is_verified: boolean
  discrepancy?: number | null
}

export interface FactualClaim {
  claim_id: string
  statement: string
  metric_references: MetricReference[]
  is_grounded: boolean
  unsupported_reason?: string | null
}

export interface CommercialHypothesis {
  hypothesis_id: string
  observation: string
  hypothesis_statement: string
  confidence: 'high' | 'medium' | 'low'
  grounding_metric_ids: string[]
}

export interface CommercialRisk {
  risk_id: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  impact_metric_id?: string | null
}

export interface ActionableRecommendation {
  recommendation_id: string
  title: string
  action: string
  expected_impact: string
  target_metric_id?: string | null
  priority: 'P1' | 'P2' | 'P3'
}

export interface ExecutiveKPIHighlight {
  label: string
  metric_id: string
  value: number
  formatted: string
  trend_direction?: 'up' | 'down' | 'neutral' | null
  context_note: string
}

export interface ExecutiveCommercialReport {
  report_title: string
  dataset_name: string
  generated_at: string
  prompt_version: string
  executive_summary: string
  kpi_highlights: ExecutiveKPIHighlight[]
  key_commercial_observations: string[]
  strategic_hypotheses: CommercialHypothesis[]
  operational_risks: CommercialRisk[]
  prioritized_recommendations: ActionableRecommendation[]
  data_quality_disclosures: string[]
  unsupported_data_disclosures: string[]
}

export interface HallucinationDetail {
  metric_id: string
  cited_value: number
  expected_value: number
  statement: string
  discrepancy_percentage: number
  severity: 'critical' | 'warning'
}

export interface VerificationResult {
  is_valid: boolean
  accuracy_score: number
  total_claims_checked: number
  verified_claims_count: number
  hallucinations: HallucinationDetail[]
  missing_evidence_warnings: string[]
  schema_errors: string[]
  repaired: boolean
  repair_notes?: string | null
}

export interface PromptChainStageResult {
  stage_number: number
  stage_name: string
  prompt_version: string
  raw_prompt: string
  raw_response: string
  parsed_output?: any
  verification: VerificationResult
  latency_ms: number
  tokens_used: number
}

export interface PromptChainExecutionResponse {
  dataset_id: string
  dataset_name: string
  prompt_version: string
  provider_name: string
  is_demo_mode: boolean
  kpi_context: Record<string, any>
  stage_1: PromptChainStageResult
  stage_2: PromptChainStageResult
  stage_3: PromptChainStageResult
  structured_report?: ExecutiveCommercialReport | null
  total_latency_ms: number
  total_tokens_used: number
  estimated_cost_usd: number
  overall_accuracy_score: number
}

export interface PromptComparisonResponse {
  dataset_id: string
  dataset_name: string
  v1_result: PromptChainExecutionResponse
  v2_result: PromptChainExecutionResponse
  accuracy_delta: number
  hallucination_reduction_pct: number
  latency_delta_ms: number
  token_delta: number
  comparison_summary: string
}

export interface EvaluationScenarioResult {
  scenario_id: string
  scenario_name: string
  version: string
  accuracy_score: number
  hallucination_count: number
  schema_valid: boolean
  refusal_correctness: boolean
  latency_ms: number
  tokens: number
  cost_usd: number
}

export interface EvaluationBenchmarkScorecard {
  evaluated_at: string
  provider_used: string
  scenarios_evaluated: number
  v1_avg_accuracy: number
  v2_avg_accuracy: number
  v1_total_hallucinations: number
  v2_total_hallucinations: number
  v1_schema_pass_rate: number
  v2_schema_pass_rate: number
  v1_refusal_pass_rate: number
  v2_refusal_pass_rate: number
  v1_avg_latency_ms: number
  v2_avg_latency_ms: number
  detailed_scenarios: EvaluationScenarioResult[]
  rubric_scores: Record<string, any>
}

// ==========================================
// Stage 6: Machine Learning Intelligence Types
// ==========================================

export interface ForecastDataPoint {
  period: string
  actual?: number | null
  forecast?: number | null
  lower_bound?: number | null
  upper_bound?: number | null
  baseline_forecast?: number | null
  is_forecast: boolean
}

export interface ForecastMetrics {
  mae: number
  rmse: number
  wape: number
  test_periods_count: number
}

export interface ModelEvaluationSummary {
  xgboost_metrics: ForecastMetrics
  baseline_metrics: ForecastMetrics
  outperforms_baseline: boolean
  wape_improvement_pct: number
  rmse_improvement_pct: number
  evaluation_verdict: string
}

export interface FeatureImportance {
  feature_name: string
  importance_score: number
}

export interface ForecastResponse {
  dataset_id: string
  dataset_name: string
  status: 'success' | 'insufficient_data' | 'error'
  message: string
  frequency: string
  historical_periods_count: number
  forecast_horizon_periods: number
  timeline: ForecastDataPoint[]
  evaluation?: ModelEvaluationSummary | null
  feature_importances: FeatureImportance[]
  model_metadata: Record<string, any>
  methodological_notes: string[]
}

export interface AnomalyRecord {
  invoice_no: string
  stock_code: string
  description: string
  quantity: number
  unit_price: number
  total_amount: number
  invoice_date: string
  customer_id: string
  country: string
  anomaly_score: number
  risk_severity: 'critical' | 'high' | 'medium' | 'low'
  suspicious_reasons: string[]
}

export interface AnomalyDistributionBucket {
  score_range: string
  count: number
  is_anomaly_zone: boolean
}

export interface AnomalyResponse {
  dataset_id: string
  dataset_name: string
  status: 'success' | 'insufficient_data' | 'error'
  message: string
  total_records_analyzed: number
  anomaly_count: number
  contamination_rate: number
  score_threshold: number
  severity_breakdown: Record<string, number>
  distribution_buckets: AnomalyDistributionBucket[]
  flagged_anomalies: AnomalyRecord[]
  model_metadata: Record<string, any>
  disclaimer: string
}


// ─── Stage 7: Knowledge Base RAG ───────────────────────────────────────────

export interface KnowledgeDocument {
  id: string
  workspace_id: string
  title: string
  original_filename: string
  file_type: 'pdf' | 'txt'
  file_size: number
  status: 'processing' | 'ready' | 'error'
  error_message?: string | null
  chunk_count: number
  created_at: string
}

export interface ChunkResult {
  chunk_id: string
  document_id: string
  document_title: string
  chunk_index: number
  chunk_text: string
  page_number?: number | null
  source_reference?: string | null
  similarity_score: number
}

export interface RetrievalResponse {
  query: string
  workspace_id: string
  chunks_found: number
  retrieved_chunks: ChunkResult[]
  retrieval_latency_ms: number
  evidence_summary: string
}


// ─── Stage 8: AI Copilot Agent ─────────────────────────────────────────────

export interface ToolExecutionTrace {
  tool_name: string
  parameters: Record<string, any>
  duration_ms: number
  status: 'success' | 'failed' | 'insufficient_data' | 'skipped'
  output_summary: string
  error_message?: string | null
}

export interface EvidenceReference {
  evidence_type: 'metric' | 'forecast' | 'anomaly' | 'document'
  reference_id: string
  title: string
  detail: string
  value?: any
}

export interface ChartPayload {
  chart_type: 'kpi_grid' | 'revenue_trends' | 'product_ranking' | 'forecast' | 'anomaly_distribution' | 'executive_summary'
  title: string
  subtitle?: string | null
  data: Record<string, any>[]
  metadata: Record<string, any>
}

export interface AgentChatRequest {
  message: string
  dataset_id: string
  session_id?: string | null
  provider_type?: string
  include_trace?: boolean
}

export interface AgentChatResponse {
  session_id: string
  response_text: string
  intent: string
  tools_executed: string[]
  execution_trace: ToolExecutionTrace[]
  evidence_references: EvidenceReference[]
  chart_payload?: ChartPayload | null
  structured_report?: Record<string, any> | null
  is_demo_mode: boolean
  total_latency_ms: number
  created_at: string
}

export interface ConversationSessionSummary {
  session_id: string
  workspace_id: string
  dataset_id: string
  title: string
  message_count: number
  created_at: string
  updated_at: string
}


// ─── Stage 9: Executive PDF Reports ────────────────────────────────────────

export interface ReportGenerateRequest {
  dataset_id: string
  prompt_version?: 'v1' | 'v2'
  title?: string
  include_forecast?: boolean
  include_anomalies?: boolean
  include_rag?: boolean
}

export interface ReportSummary {
  id: string
  workspace_id: string
  dataset_id: string
  title: string
  prompt_version: string
  file_size_bytes: number
  format: string
  status: string
  created_at: string
}

export interface ReportDetail {
  id: string
  workspace_id: string
  dataset_id: string
  title: string
  prompt_version: string
  file_size_bytes: number
  format: string
  status: string
  download_url: string
  report_metadata?: Record<string, any> | null
  created_at: string
}
