"""Tests for Evidence-Grounded Prompt Engineering Engine."""
import pytest
from app.services.llm_provider import (
    LocalDeterministicLLMProvider, OpenAILLMProvider, GeminiLLMProvider, get_llm_provider
)
from app.services.verification_engine import VerificationEngine
from app.services.prompt_service import PromptService


@pytest.fixture
def sample_kpis():
    return {
        "total_revenue": 100000.0,
        "unique_orders": 500,
        "units_sold": 15000,
        "average_order_value": 200.0,
        "unique_customers": 120,
        "cancellation_rate": 5.0,
        "top_product": "Widget Pro",
        "top_product_revenue": 30000.0,
        "top_country": "Germany",
        "top_country_revenue": 45000.0,
    }


class TestLLMProviderAbstraction:
    """Test provider abstraction and deterministic demo mode."""

    def test_local_deterministic_provider_generation(self, sample_kpis):
        provider = LocalDeterministicLLMProvider()
        resp = provider.generate(
            prompt="Summarize metrics",
            stage_hint="stage_1",
            prompt_version="v2",
            kpi_context=sample_kpis,
        )
        assert resp.model_name == "deterministic-local-demo"
        assert resp.provider_type == "local_demo"
        assert resp.cost_estimate_usd == 0.0
        assert resp.total_tokens > 0
        assert resp.latency_ms > 0
        assert "CLM-001" in resp.text
        assert "total_revenue" in resp.text

    def test_provider_factory(self):
        provider = get_llm_provider("local_demo")
        assert isinstance(provider, LocalDeterministicLLMProvider)

    def test_cloud_providers_raise_without_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        openai_p = OpenAILLMProvider(api_key="")
        gemini_p = GeminiLLMProvider(api_key="")

        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            openai_p.generate("test")

        with pytest.raises(ValueError, match="Gemini API key not configured"):
            gemini_p.generate("test")


class TestVerificationEngine:
    """Test numeric claim verification and hallucination detection."""

    def test_verify_stage1_exact_match(self, sample_kpis):
        engine = VerificationEngine(sample_kpis)
        raw_json = """
        [
          {
            "claim_id": "CLM-001",
            "statement": "Net revenue reached $100,000.00.",
            "metric_references": [{"metric_id": "total_revenue", "cited_value": 100000.0}]
          }
        ]
        """
        output, v_res = engine.verify_stage1_factual(raw_json)
        assert v_res.is_valid is True
        assert v_res.accuracy_score == 100.0
        assert len(v_res.hallucinations) == 0
        assert v_res.verified_claims_count == 1

    def test_detect_hallucinated_numeric_value(self, sample_kpis):
        engine = VerificationEngine(sample_kpis)
        # Expected total_revenue is 100000.0; cited is 150000.0 (50% discrepancy)
        raw_json = """
        [
          {
            "claim_id": "CLM-001",
            "statement": "Net revenue reached $150,000.00.",
            "metric_references": [{"metric_id": "total_revenue", "cited_value": 150000.0}]
          }
        ]
        """
        output, v_res = engine.verify_stage1_factual(raw_json)
        assert v_res.is_valid is False
        assert v_res.accuracy_score == 0.0
        assert len(v_res.hallucinations) == 1
        assert v_res.hallucinations[0].discrepancy_percentage == 50.0

    def test_detect_unknown_metric_id(self, sample_kpis):
        engine = VerificationEngine(sample_kpis)
        raw_json = """
        [
          {
            "claim_id": "CLM-001",
            "statement": "Gross margin was 35%.",
            "metric_references": [{"metric_id": "gross_margin_percentage", "cited_value": 35.0}]
          }
        ]
        """
        output, v_res = engine.verify_stage1_factual(raw_json)
        assert v_res.is_valid is False
        assert len(v_res.hallucinations) == 1
        assert v_res.hallucinations[0].metric_id == "gross_margin_percentage"

    def test_stage2_hypotheses_and_refusal_check(self, sample_kpis):
        engine = VerificationEngine(sample_kpis)
        valid_stage2 = """
        {
          "insights_text": "Executive assessment",
          "hypotheses": [
            {
              "hypothesis_id": "HYP-001",
              "observation": "High order volume",
              "hypothesis_statement": "[HYPOTHESIS] Bulk purchasing trend",
              "confidence": "high",
              "grounding_metric_ids": ["total_revenue"]
            }
          ],
          "risks": [
            {
              "risk_id": "RSK-001",
              "description": "Territory risk",
              "severity": "medium",
              "impact_metric_id": "total_revenue"
            }
          ],
          "recommendations": [
            {
              "recommendation_id": "REC-001",
              "title": "Stock Buffering",
              "action": "Buffer inventory",
              "expected_impact": "Reduce stockouts",
              "target_metric_id": "units_sold",
              "priority": "P1"
            }
          ],
          "unsupported_factors_noted": [
            "Gross profit: Insufficient data (no COGS)"
          ]
        }
        """
        output, v_res = engine.verify_stage2_insights(valid_stage2)
        assert v_res.is_valid is True
        assert v_res.accuracy_score == 100.0

    def test_stage3_strict_schema_validation(self, sample_kpis):
        engine = VerificationEngine(sample_kpis)
        valid_stage3 = f"""
        {{
          "report_title": "Executive Commercial Intelligence Report",
          "dataset_name": "Test Dataset",
          "generated_at": "2026-11-17T00:00:00Z",
          "prompt_version": "v2",
          "executive_summary": "Summary text here.",
          "kpi_highlights": [
            {{
              "label": "Total Revenue",
              "metric_id": "total_revenue",
              "value": 100000.0,
              "formatted": "$100,000.00",
              "trend_direction": "up",
              "context_note": "Net"
            }}
          ],
          "key_commercial_observations": ["Obs 1"],
          "strategic_hypotheses": [],
          "operational_risks": [],
          "prioritized_recommendations": [],
          "data_quality_disclosures": ["Audited clean"],
          "unsupported_data_disclosures": ["Margins: Insufficient data"]
        }}
        """
        report, v_res = engine.verify_stage3_report(valid_stage3)
        assert report is not None
        assert v_res.is_valid is True
        assert report.report_title == "Executive Commercial Intelligence Report"


class TestPromptService:
    """Test 3-stage chained prompt pipeline execution and comparisons."""

    def test_execute_chain_v2(self, sample_kpis):
        service = PromptService()
        result = service.execute_chain(
            dataset_id="test-ds-1",
            dataset_name="Test Wholesale",
            kpi_data=sample_kpis,
            prompt_version="v2",
        )
        assert result.dataset_id == "test-ds-1"
        assert result.prompt_version == "v2"
        assert result.is_demo_mode is True
        assert result.stage_1.stage_number == 1
        assert result.stage_2.stage_number == 2
        assert result.stage_3.stage_number == 3
        assert result.structured_report is not None
        assert result.overall_accuracy_score == 100.0
        assert result.total_latency_ms > 0
        assert result.total_tokens_used > 0

    def test_compare_v1_and_v2(self, sample_kpis):
        service = PromptService()
        comparison = service.compare_versions(
            dataset_id="test-ds-1",
            dataset_name="Test Wholesale",
            kpi_data=sample_kpis,
        )
        assert comparison.v1_result.prompt_version == "v1"
        assert comparison.v2_result.prompt_version == "v2"
        assert comparison.v2_result.overall_accuracy_score >= comparison.v1_result.overall_accuracy_score
        assert "Prompt v2 improved" in comparison.comparison_summary
