import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from urllib.parse import urlparse

# Reusing the extraction schema definition for typing
from app.services.extraction_agent import ExtractedOpportunity

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class ValidationAuditLog(BaseModel):
    step: str
    message: str
    points_deducted: float = 0.0

class ValidationResult(BaseModel):
    opportunity_id: str # Represents the DB row ID
    source_score: float = 0.0
    deadline_score: float = 0.0
    duplicate_score: float = 0.0
    eligibility_score: float = 0.0
    benefit_score: float = 0.0
    document_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    trust_score: float = 0.0
    quality_score: float = 0.0
    validation_confidence: float = 0.0
    overall_validation_score: float = 0.0
    validation_status: str = "Pending"
    validation_reason: str = ""
    audit_trail: List[ValidationAuditLog] = []

# ==========================================
# 2. VALIDATION ENGINE
# ==========================================
class OpportunityValidationEngine:
    """
    STAGE 7: The Quality Control Layer
    Mathematically validates extracted opportunities across 12 distinct engines.
    """

    def process_validation_queue(self, extracted_opportunities: List[Dict[str, Any]]) -> List[ValidationResult]:
        results = []
        for raw_dict in extracted_opportunities:
            # Reconstruct the Pydantic model
            try:
                opp = ExtractedOpportunity(**raw_dict["extracted_data"])
                db_id = raw_dict["id"]
                source_url = raw_dict.get("source_url", "")
                
                result = self._validate_single(opp, db_id, source_url)
                results.append(result)
            except Exception as e:
                # If it completely fails to parse, auto reject
                results.append(ValidationResult(
                    opportunity_id=str(raw_dict.get("id", "unknown")),
                    validation_status="Rejected",
                    validation_reason=f"Failed to parse extraction payload: {str(e)}"
                ))
        return results

    def _validate_single(self, opp: ExtractedOpportunity, db_id: str, source_url: str) -> ValidationResult:
        result = ValidationResult(opportunity_id=str(db_id))
        
        # 1. Source
        result.source_score = self._engine_1_source(source_url, result)
        if result.source_score < 30:
            return self._quick_reject(result, "Source Trust too low.")

        # 2. Deadline
        result.deadline_score = self._engine_2_deadline(opp, result)
        if result.deadline_score == 0:
             return self._quick_reject(result, "Deadline expired.")

        # 3. Duplicate
        result.duplicate_score = self._engine_3_duplicate(opp, result)
        if result.duplicate_score == 100:
             result.validation_status = "Merged"
             result.validation_reason = "Exact duplicate merged with existing record."
             return result

        # 4. Eligibility
        result.eligibility_score = self._engine_4_eligibility(opp, result)

        # 5. Benefits
        result.benefit_score = self._engine_5_benefit(opp, result)
        if result.benefit_score == 0:
             return self._quick_reject(result, "No clear benefits extracted.")

        # 6. Documents
        result.document_score = self._engine_6_document(opp, result)

        # 7. Completeness
        result.completeness_score = self._engine_7_completeness(opp, result)

        # 8. Consistency
        result.consistency_score = self._engine_8_consistency(opp, result)

        # 9. Classification (Mock check)
        self._engine_9_classification(opp, result)

        # 10. Trust Engine
        result.trust_score = result.source_score

        # 11. Quality Engine
        result.quality_score = (result.completeness_score + result.consistency_score + result.benefit_score + result.eligibility_score) / 4.0

        # 12. Confidence Engine
        gemini_conf = opp.confidence_metrics.get("overall_confidence", 80.0)
        result.validation_confidence = (gemini_conf + result.quality_score) / 2.0

        # FINAL MATH FORMULA
        final_score = (
            (result.source_score * 0.25) +
            (result.deadline_score * 0.15) +
            (result.eligibility_score * 0.15) +
            (result.benefit_score * 0.15) +
            (result.document_score * 0.10) +
            (result.completeness_score * 0.10) +
            (result.consistency_score * 0.10)
        )
        result.overall_validation_score = round(final_score, 2)

        # APPROVAL LOGIC
        if final_score >= 85:
            result.validation_status = "Approved"
            result.validation_reason = "Passed all mathematical QC checks."
        elif final_score >= 60:
            result.validation_status = "Review Required"
            result.validation_reason = "Score fell below automatic approval threshold."
        else:
            result.validation_status = "Rejected"
            result.validation_reason = f"Final score ({result.overall_validation_score}) below 60."

        return result

    def _quick_reject(self, result: ValidationResult, reason: str) -> ValidationResult:
        result.validation_status = "Rejected"
        result.validation_reason = reason
        return result

    # --- ENGINES ---

    def _engine_1_source(self, url: str, result: ValidationResult) -> float:
        domain = urlparse(url).netloc.lower()
        if domain.endswith(".gov.in") or domain.endswith(".nic.in") or domain == "india.gov.in":
            return 100.0
        elif "aicte" in domain or "ugc" in domain:
            return 95.0
        elif domain.endswith(".ac.in") or domain.endswith(".edu.in"):
            return 90.0
        elif domain.endswith(".org") or domain.endswith(".org.in"):
            return 80.0
        elif domain.endswith(".com") or domain.endswith(".in"):
            return 70.0
        return 10.0 # Blog/Unknown

    def _engine_2_deadline(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        deadline_str = opp.deadlines.get("application_deadline")
        if not deadline_str:
            result.audit_trail.append(ValidationAuditLog(step="Deadline", message="No explicit deadline found. Defaulting to rolling (40 points)."))
            return 40.0
        try:
            deadline_date = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
            today = datetime.datetime.now().date()
            diff = (deadline_date - today).days
            if diff < 0:
                result.audit_trail.append(ValidationAuditLog(step="Deadline", message="Deadline is in the past."))
                return 0.0
            if diff > 7:
                return 100.0
            return 80.0
        except ValueError:
            return 40.0

    def _engine_3_duplicate(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        # In production, runs a DB query. We mock it as unique.
        return 0.0

    def _engine_4_eligibility(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        score = 0.0
        if opp.eligibility.income_limits is not None: score += 25
        if opp.eligibility.age_requirements: score += 25
        if opp.eligibility.location_requirements: score += 25
        if opp.eligibility.category_restrictions: score += 25
        
        if score == 0:
            result.audit_trail.append(ValidationAuditLog(step="Eligibility", message="No structured eligibility conditions found."))
            return 0.0
        return score

    def _engine_5_benefit(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        if opp.benefits.financial_value is not None and opp.benefits.financial_value > 0:
            return 100.0
        if opp.benefits.benefit_summary and len(opp.benefits.benefit_summary) > 10:
            return 80.0
        return 30.0

    def _engine_6_document(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        req = opp.documents.get("required", [])
        if len(req) > 2:
            return 100.0
        if len(req) > 0:
            return 70.0
        return 0.0

    def _engine_7_completeness(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        fields = [
            opp.opportunity_title, opp.provider_name, opp.description, 
            opp.application.get("apply_link")
        ]
        valid = sum(1 for f in fields if f)
        return (valid / len(fields)) * 100.0

    def _engine_8_consistency(self, opp: ExtractedOpportunity, result: ValidationResult) -> float:
        # Check if Apply link exists when active
        if opp.deadlines.get("is_active") == "true" and not opp.application.get("apply_link"):
            result.audit_trail.append(ValidationAuditLog(step="Consistency", message="Active scheme lacks apply link.", points_deducted=50.0))
            return 50.0
        return 100.0

    def _engine_9_classification(self, opp: ExtractedOpportunity, result: ValidationResult):
        # Simply verifies it's not empty
        if not opp.opportunity_type:
            result.audit_trail.append(ValidationAuditLog(step="Classification", message="Missing opportunity type."))
