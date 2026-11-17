"""Pydantic schemas for the Evidence-Grounded Prompt Engineering Engine."""
from pydantic import BaseModel, Field
from typing import Optional, Any, Literal


class MetricReference(BaseModel):
    """Structured metric reference linking a claim to verified deterministic KPI."""
    metric_id: str = Field(..., description="Canonical ID of verified KPI, e.g. total_revenue")
    cited_value: float = Field(..., description="Numerical value stated in the narrative")
    formatted_value: Optional[str] = None
    is_verified: bool = False
    discrepancy: Optional[float] = None


class FactualClaim(BaseModel):
    """Individual factual statement extracted from Stage 1 output."""
    claim_id: str
    statement: str
    metric_references: list[MetricReference] = []
    is_grounded: bool = True
    unsupported_reason: Optional[str] = None


class Stage1FactualOutput(BaseModel):
    """Validated output from Stage 1: Factual Data Summarization."""
    summary_text: str
    claims: list[FactualClaim] = []
    total_metrics_cited: int = 0
    grounding_score: float = 100.0


class CommercialHypothesis(BaseModel):
    """Explicitly labeled hypothesis from Stage 2."""
    hypothesis_id: str
    observation: str
    hypothesis_statement: str
    confidence: Literal["high", "medium", "low"] = "medium"
    grounding_metric_ids: list[str] = []


class CommercialRisk(BaseModel):
    """Identified commercial risk from Stage 2."""
    risk_id: str
    description: str
    severity: Literal["critical", "high", "medium", "low"] = "medium"
    impact_metric_id: Optional[str] = None


class ActionableRecommendation(BaseModel):
    """Concrete business recommendation from Stage 2."""
    recommendation_id: str
    title: str
    action: str
    expected_impact: str
    target_metric_id: Optional[str] = None
    priority: Literal["P1", "P2", "P3"] = "P2"


class Stage2InsightsOutput(BaseModel):
    """Validated output from Stage 2: Business Insights & Recommendations."""
    insights_text: str
    hypotheses: list[CommercialHypothesis] = []
    risks: list[CommercialRisk] = []
    recommendations: list[ActionableRecommendation] = []
    unsupported_factors_noted: list[str] = []  # Explicit "Insufficient data" items


class ExecutiveKPIHighlight(BaseModel):
    """High-level KPI highlight for executive review."""
    label: str
    metric_id: str
    value: float
    formatted: str
    trend_direction: Optional[Literal["up", "down", "neutral"]] = None
    context_note: str


class ExecutiveCommercialReport(BaseModel):
    """Strict JSON schema for Stage 3: Structured Executive Commercial Report."""
    report_title: str = "Executive Commercial Intelligence Report"
    dataset_name: str
    generated_at: str
    prompt_version: str
    executive_summary: str
    kpi_highlights: list[ExecutiveKPIHighlight] = []
    key_commercial_observations: list[str] = []
    strategic_hypotheses: list[CommercialHypothesis] = []
    operational_risks: list[CommercialRisk] = []
    prioritized_recommendations: list[ActionableRecommendation] = []
    data_quality_disclosures: list[str] = []
    unsupported_data_disclosures: list[str] = []


class HallucinationDetail(BaseModel):
    """Detail of a detected numerical or factual hallucination."""
    metric_id: str
    cited_value: float
    expected_value: float
    statement: str
    discrepancy_percentage: float
    severity: Literal["critical", "warning"] = "critical"


class VerificationResult(BaseModel):
    """Comprehensive verification audit result."""
    is_valid: bool = True
    accuracy_score: float = 100.0  # 0 to 100
    total_claims_checked: int = 0
    verified_claims_count: int = 0
    hallucinations: list[HallucinationDetail] = []
    missing_evidence_warnings: list[str] = []
    schema_errors: list[str] = []
    repaired: bool = False
    repair_notes: Optional[str] = None


class PromptChainStageResult(BaseModel):
    """Result of a single stage execution in the chain."""
    stage_number: int
    stage_name: str
    prompt_version: str
    raw_prompt: str
    raw_response: str
    parsed_output: Optional[Any] = None
    verification: VerificationResult
    latency_ms: float
    tokens_used: int = 0


class PromptChainExecutionResponse(BaseModel):
    """Full execution response of the 3-stage prompt chain."""
    dataset_id: str
    dataset_name: str
    prompt_version: str  # "v1" or "v2"
    provider_name: str
    is_demo_mode: bool = True
    kpi_context: dict[str, Any]
    stage_1: PromptChainStageResult
    stage_2: PromptChainStageResult
    stage_3: PromptChainStageResult
    structured_report: Optional[ExecutiveCommercialReport] = None
    rag_evidence: Optional[dict[str, Any]] = None
    total_latency_ms: float
    total_tokens_used: int
    estimated_cost_usd: float
    overall_accuracy_score: float


class PromptComparisonResponse(BaseModel):
    """Side-by-side comparison between Prompt v1 and Prompt v2."""
    dataset_id: str
    dataset_name: str
    v1_result: PromptChainExecutionResponse
    v2_result: PromptChainExecutionResponse
    accuracy_delta: float
    hallucination_reduction_pct: float
    latency_delta_ms: float
    token_delta: int
    comparison_summary: str


class EvaluationScenarioResult(BaseModel):
    """Evaluation result on a single golden scenario."""
    scenario_id: str
    scenario_name: str
    version: str
    accuracy_score: float
    hallucination_count: int
    schema_valid: bool
    refusal_correctness: bool
    latency_ms: float
    tokens: int
    cost_usd: float


class EvaluationBenchmarkScorecard(BaseModel):
    """Aggregated evaluation scorecard comparing v1 and v2 across golden datasets."""
    evaluated_at: str
    provider_used: str
    scenarios_evaluated: int
    v1_avg_accuracy: float
    v2_avg_accuracy: float
    v1_total_hallucinations: int
    v2_total_hallucinations: int
    v1_schema_pass_rate: float
    v2_schema_pass_rate: float
    v1_refusal_pass_rate: float
    v2_refusal_pass_rate: float
    v1_avg_latency_ms: float
    v2_avg_latency_ms: float
    detailed_scenarios: list[EvaluationScenarioResult] = []
    rubric_scores: dict[str, Any] = {}
