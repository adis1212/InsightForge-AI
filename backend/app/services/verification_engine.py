"""Deterministic Verification Engine for LLM outputs.

Validates numeric claims against verified Pandas metric IDs, checks evidence citations,
verifies JSON schemas against Pydantic models, detects hallucinations, and performs
deterministic output repair.
"""
import re
import json
from typing import Any, Optional
from pydantic import ValidationError as PydanticValidationError

from app.schemas.prompt_schemas import (
    VerificationResult, HallucinationDetail, ExecutiveCommercialReport,
    Stage1FactualOutput, Stage2InsightsOutput
)


class VerificationEngine:
    """Verifies and validates LLM generation artifacts against deterministic ground truth."""

    # Default tolerance for floating point / currency differences
    FLOAT_TOLERANCE_PCT = 0.5  # 0.5% tolerance for rounding in formatted currency

    def __init__(self, ground_truth_kpis: dict[str, Any]):
        """
        Initialize with verified deterministic KPIs from Pandas.
        
        Args:
            ground_truth_kpis: Dict mapping metric_id -> numeric value
        """
        self.ground_truth = ground_truth_kpis

    def clean_json_markdown(self, raw_text: str) -> str:
        """Strip markdown code fence wrappers (```json ... ```) if present."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def verify_stage1_factual(self, raw_output: str, prompt_version: str = "v2") -> tuple[Stage1FactualOutput, VerificationResult]:
        """
        Verify Stage 1 Factual Data Summarization output.
        Checks that every cited metric ID exists and the cited value matches ground truth.
        """
        cleaned_json = self.clean_json_markdown(raw_output)
        hallucinations: list[HallucinationDetail] = []
        schema_errors: list[str] = []
        missing_evidence: list[str] = []
        repaired = False
        parsed_claims = []

        total_claims_checked = 0
        verified_claims_count = 0

        # Attempt to parse structured JSON
        try:
            data = json.loads(cleaned_json)
            if isinstance(data, list):
                for item in data:
                    total_claims_checked += 1
                    claim_id = item.get("claim_id", f"CLM-{total_claims_checked:03d}")
                    statement = item.get("statement", "")
                    refs = item.get("metric_references", [])

                    if not refs:
                        missing_evidence.append(f"Claim '{claim_id}' cites no structured metric references.")

                    claim_valid = True
                    for ref in refs:
                        metric_id = ref.get("metric_id")
                        cited_val = ref.get("cited_value")

                        if metric_id not in self.ground_truth:
                            claim_valid = False
                            hallucinations.append(HallucinationDetail(
                                metric_id=str(metric_id),
                                cited_value=float(cited_val or 0.0),
                                expected_value=0.0,
                                statement=statement,
                                discrepancy_percentage=100.0,
                                severity="critical"
                            ))
                        else:
                            expected_val = float(self.ground_truth[metric_id])
                            discrepancy = abs(float(cited_val) - expected_val)
                            pct_diff = (discrepancy / expected_val * 100) if expected_val != 0 else discrepancy

                            if pct_diff > self.FLOAT_TOLERANCE_PCT:
                                claim_valid = False
                                hallucinations.append(HallucinationDetail(
                                    metric_id=metric_id,
                                    cited_value=float(cited_val),
                                    expected_value=expected_val,
                                    statement=statement,
                                    discrepancy_percentage=round(pct_diff, 2),
                                    severity="critical"
                                ))
                            else:
                                ref["is_verified"] = True

                    if claim_valid and refs:
                        verified_claims_count += 1

                    parsed_claims.append({
                        "claim_id": claim_id,
                        "statement": statement,
                        "metric_references": refs,
                        "is_grounded": claim_valid
                    })
            else:
                schema_errors.append("Stage 1 output is not a JSON list of claims.")
        except json.JSONDecodeError:
            # v1 baseline or unformatted text: extract claims via regex
            repaired = True
            lines = [l.strip() for l in raw_output.split("\n") if l.strip()]
            for idx, line in enumerate(lines, 1):
                total_claims_checked += 1
                # Check for numbers in line
                nums = re.findall(r"\$?\b\d[\d,]*\.?\d*\b", line)
                if nums:
                    missing_evidence.append(f"Line {idx} contains numbers without structured metric ID reference.")
                parsed_claims.append({
                    "claim_id": f"RAW-{idx:03d}",
                    "statement": line,
                    "metric_references": [],
                    "is_grounded": False
                })

        accuracy = 100.0
        if total_claims_checked > 0:
            accuracy = max(0.0, round((verified_claims_count / total_claims_checked) * 100.0, 1))

        v_result = VerificationResult(
            is_valid=(len(hallucinations) == 0 and len(schema_errors) == 0 and len(missing_evidence) == 0),
            accuracy_score=accuracy,
            total_claims_checked=total_claims_checked,
            verified_claims_count=verified_claims_count,
            hallucinations=hallucinations,
            missing_evidence_warnings=missing_evidence,
            schema_errors=schema_errors,
            repaired=repaired,
            repair_notes="Parsed raw text into structured claim objects" if repaired else None
        )

        stage1_output = Stage1FactualOutput(
            summary_text=raw_output,
            claims=parsed_claims,
            total_metrics_cited=verified_claims_count,
            grounding_score=accuracy
        )

        return stage1_output, v_result

    def verify_stage2_insights(self, raw_output: str, prompt_version: str = "v2") -> tuple[Stage2InsightsOutput, VerificationResult]:
        """
        Verify Stage 2 Business Insights & Recommendations output.
        Checks hypothesis labeling, risk metric anchoring, and 'Insufficient data' refusal handling.
        """
        cleaned_json = self.clean_json_markdown(raw_output)
        hallucinations: list[HallucinationDetail] = []
        schema_errors: list[str] = []
        missing_evidence: list[str] = []
        repaired = False

        total_items = 0
        valid_items = 0

        try:
            data = json.loads(cleaned_json)
            stage2_obj = Stage2InsightsOutput.model_validate(data)

            # Check hypotheses
            for hyp in stage2_obj.hypotheses:
                total_items += 1
                if not hyp.hypothesis_statement.startswith("[HYPOTHESIS]"):
                    missing_evidence.append(f"Hypothesis {hyp.hypothesis_id} lacks explicit '[HYPOTHESIS]' prefix.")
                else:
                    valid_items += 1

            # Check risks
            for rsk in stage2_obj.risks:
                total_items += 1
                if rsk.impact_metric_id and rsk.impact_metric_id not in self.ground_truth:
                    hallucinations.append(HallucinationDetail(
                        metric_id=rsk.impact_metric_id,
                        cited_value=0.0,
                        expected_value=0.0,
                        statement=rsk.description,
                        discrepancy_percentage=100.0,
                        severity="warning"
                    ))
                else:
                    valid_items += 1

            # Check recommendations
            for rec in stage2_obj.recommendations:
                total_items += 1
                if rec.target_metric_id and rec.target_metric_id not in self.ground_truth:
                    missing_evidence.append(f"Recommendation {rec.recommendation_id} targets unknown metric '{rec.target_metric_id}'.")
                else:
                    valid_items += 1

            # Check refusal on missing data (profit margins / causes)
            if not stage2_obj.unsupported_factors_noted:
                missing_evidence.append("Missing explicit 'Insufficient data' disclosures for unsupported factors.")

        except (json.JSONDecodeError, PydanticValidationError) as e:
            # v1 or invalid formatting
            repaired = True
            schema_errors.append(f"Stage 2 schema validation failed: {str(e)[:150]}")
            stage2_obj = Stage2InsightsOutput(
                insights_text=raw_output,
                hypotheses=[],
                risks=[],
                recommendations=[],
                unsupported_factors_noted=["Refusal not properly formatted."]
            )
            total_items = 1

        accuracy = max(0.0, round((valid_items / max(1, total_items)) * 100.0, 1))

        v_result = VerificationResult(
            is_valid=(len(hallucinations) == 0 and len(schema_errors) == 0 and len(missing_evidence) == 0),
            accuracy_score=accuracy,
            total_claims_checked=total_items,
            verified_claims_count=valid_items,
            hallucinations=hallucinations,
            missing_evidence_warnings=missing_evidence,
            schema_errors=schema_errors,
            repaired=repaired,
            repair_notes="Standardized unformatted insights into fallback schema" if repaired else None
        )

        return stage2_obj, v_result

    def verify_stage3_report(self, raw_output: str, prompt_version: str = "v2") -> tuple[Optional[ExecutiveCommercialReport], VerificationResult]:
        """
        Verify Stage 3 Structured Report output against ExecutiveCommercialReport Pydantic schema.
        Validates KPI highlights against ground truth and performs auto-repair when possible.
        """
        cleaned_json = self.clean_json_markdown(raw_output)
        hallucinations: list[HallucinationDetail] = []
        schema_errors: list[str] = []
        missing_evidence: list[str] = []
        repaired = False
        report: Optional[ExecutiveCommercialReport] = None

        total_kpis = 0
        valid_kpis = 0

        # Attempt parse and repair
        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError:
            repaired = True
            # Attempt regex extraction of JSON block
            match = re.search(r"\{[\s\S]*\}", raw_output)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError as err:
                    schema_errors.append(f"JSON syntax error: {str(err)}")
                    data = None
            else:
                schema_errors.append("No valid JSON structure found in Stage 3 output.")
                data = None

        if data:
            # Check KPI highlights against ground truth
            kpis = data.get("kpi_highlights", [])
            for k in kpis:
                total_kpis += 1
                metric_id = k.get("metric_id")
                cited_val = k.get("value")

                if metric_id in self.ground_truth:
                    expected = float(self.ground_truth[metric_id])
                    try:
                        cited = float(cited_val)
                        diff = abs(cited - expected)
                        pct = (diff / expected * 100) if expected != 0 else diff
                        if pct > self.FLOAT_TOLERANCE_PCT:
                            hallucinations.append(HallucinationDetail(
                                metric_id=metric_id,
                                cited_value=cited,
                                expected_value=expected,
                                statement=f"KPI highlight '{k.get('label')}'",
                                discrepancy_percentage=round(pct, 2),
                                severity="critical"
                            ))
                            # Auto-repair metric value
                            k["value"] = expected
                            repaired = True
                        else:
                            valid_kpis += 1
                    except (ValueError, TypeError):
                        schema_errors.append(f"Invalid numeric value '{cited_val}' for metric '{metric_id}'.")
                else:
                    hallucinations.append(HallucinationDetail(
                        metric_id=str(metric_id),
                        cited_value=float(cited_val or 0.0),
                        expected_value=0.0,
                        statement=f"Unknown metric '{metric_id}' in KPI highlights",
                        discrepancy_percentage=100.0,
                        severity="critical"
                    ))

            # Validate against strict Pydantic model
            try:
                report = ExecutiveCommercialReport.model_validate(data)
            except PydanticValidationError as err:
                schema_errors.append(f"Schema validation errors: {err.error_count()} fields violated.")

        accuracy = max(0.0, round((valid_kpis / max(1, total_kpis)) * 100.0, 1))

        v_result = VerificationResult(
            is_valid=(len(hallucinations) == 0 and len(schema_errors) == 0 and len(missing_evidence) == 0),
            accuracy_score=accuracy,
            total_claims_checked=total_kpis,
            verified_claims_count=valid_kpis,
            hallucinations=hallucinations,
            missing_evidence_warnings=missing_evidence,
            schema_errors=schema_errors,
            repaired=repaired,
            repair_notes="Repaired markdown wrappers and injected ground truth values" if repaired else None
        )

        return report, v_result
