import difflib
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

from app.services.extraction_agent import ExtractedOpportunity
from app.models.opportunity import Opportunity
from app.models.fusion import OpportunityChangeLog, OpportunityVersion, OpportunitySourceMap, OpportunityAlias

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class FusionResult(BaseModel):
    master_opportunity_id: str
    action_taken: str # "CREATED", "MERGED", "ENRICHED"
    duplicate_confidence: float
    fields_updated: List[str] = []
    version_incremented: bool = False

# ==========================================
# 2. KNOWLEDGE FUSION ENGINE
# ==========================================
class KnowledgeFusionEngine:
    """
    STAGE 8: Opportunity Knowledge Fusion Engine
    The MDM Layer preventing duplicate pollution and actively enriching Master Records.
    """
    
    def __init__(self):
        # Mocking an in-memory database of the 113 verified opportunities
        self.master_db_mock = [
            {
                "id": 1,
                "title": "PM Kisan Samman Nidhi",
                "provider_name": "Government of India",
                "apply_link": "https://pmkisan.gov.in",
                "benefits": {"financial_value": 6000.0, "benefit_summary": "6000 per year"},
                "documents": {"required": ["Aadhaar"], "optional": []},
                "deadlines": {"application_deadline": None, "is_active": "true"},
                "eligibility": {"location_requirements": [], "category_restrictions": []}
            }
        ]
        
        # Mock Alias Table
        self.alias_table = {
            "pm kisan": 1,
            "pm-kisan": 1,
            "pradhan mantri kisan samman nidhi": 1
        }

    def execute_fusion(self, new_opp: ExtractedOpportunity, source_id: int) -> FusionResult:
        """Main Pipeline execution."""
        
        # Step 1: Alias & Duplicate Detection
        master_id, confidence = self._detect_duplicate(new_opp)
        
        if confidence >= 70 and master_id is not None:
            # We found a match. ENRICH DO NOT CREATE.
            return self._enrich_master_record(master_id, new_opp, source_id, confidence)
        else:
            # Step 2: Create brand new Master Record
            return self._create_new_master(new_opp, source_id)

    # --- ENGINES ---

    def _detect_duplicate(self, new_opp: ExtractedOpportunity) -> Tuple[Optional[int], float]:
        """Engine 1 & 2: Fuzzy matching and Alias resolution."""
        title_lower = new_opp.opportunity_title.lower()
        
        # Check Alias Engine first (O(1) resolution)
        if title_lower in self.alias_table:
            return self.alias_table[title_lower], 95.0
            
        # Fallback to Fuzzy Matching against Master DB
        highest_score = 0.0
        best_match_id = None
        
        for master in self.master_db_mock:
            # Jaro-Winkler/SequenceMatcher mock
            sim = difflib.SequenceMatcher(None, title_lower, master["title"].lower()).ratio() * 100
            
            # Boost if provider matches
            if new_opp.provider_name.lower() == master["provider_name"].lower():
                sim += 15.0
                
            # Boost if apply link matches EXACTLY
            if new_opp.application.get("apply_link") == master["apply_link"]:
                sim += 30.0
                
            if sim > highest_score:
                highest_score = min(sim, 100.0)
                best_match_id = master["id"]
                
        if highest_score >= 70.0:
            return best_match_id, highest_score
            
        return None, 0.0

    def _enrich_master_record(self, master_id: int, new_opp: ExtractedOpportunity, source_id: int, confidence: float) -> FusionResult:
        """Engine 3-9: Merges missing data gracefully."""
        # Fetch Master Record (Mock)
        master = next((m for m in self.master_db_mock if m["id"] == master_id), None)
        if not master:
            return FusionResult(master_opportunity_id=str(master_id), action_taken="ERROR", duplicate_confidence=0.0)
            
        fields_updated = []
        
        # Snapshot for Version Control (Engine 13)
        old_snapshot = json.dumps(master)
        
        # Engine 5: Deadline Update
        new_deadline = new_opp.deadlines.get("application_deadline")
        old_deadline = master["deadlines"].get("application_deadline")
        if new_deadline and (old_deadline is None or new_deadline != old_deadline):
            self._log_change(master_id, "deadline", str(old_deadline), str(new_deadline), source_id)
            master["deadlines"]["application_deadline"] = new_deadline
            fields_updated.append("deadline")

        # Engine 6: Benefit Update
        new_val = new_opp.benefits.financial_value
        old_val = master["benefits"].get("financial_value")
        if new_val is not None and (old_val is None or old_val == 0.0):
            self._log_change(master_id, "benefit_value", str(old_val), str(new_val), source_id)
            master["benefits"]["financial_value"] = new_val
            fields_updated.append("benefits")

        # Engine 7: Document Enrichment (List Union)
        new_docs = new_opp.documents.get("required", [])
        old_docs = master["documents"].get("required", [])
        union_docs = list(set(old_docs + new_docs))
        if len(union_docs) > len(old_docs):
            self._log_change(master_id, "required_documents", str(old_docs), str(union_docs), source_id)
            master["documents"]["required"] = union_docs
            fields_updated.append("documents")

        # Engine 4: Source Aggregation
        self._map_source(master_id, source_id)
        
        # Engine 13: Version Control
        version_incremented = False
        if fields_updated:
            self._snapshot_version(master_id, json.loads(old_snapshot))
            version_incremented = True
            
        return FusionResult(
            master_opportunity_id=str(master_id),
            action_taken="ENRICHED",
            duplicate_confidence=confidence,
            fields_updated=fields_updated,
            version_incremented=version_incremented
        )

    def _create_new_master(self, new_opp: ExtractedOpportunity, source_id: int) -> FusionResult:
        """Handles completely unique opportunities."""
        # In production: DB Insert into `opportunities`
        new_id = 999 
        
        # Engine 4: Map source
        self._map_source(new_id, source_id)
        
        return FusionResult(
            master_opportunity_id=str(new_id),
            action_taken="CREATED",
            duplicate_confidence=0.0,
            fields_updated=["ALL"],
            version_incremented=False
        )

    # --- VERSION & CHANGE LOGGING ---

    def _log_change(self, opp_id: int, field: str, old_val: str, new_val: str, source_id: int):
        """Engine 12: Atomic Change Detection Logging."""
        log = OpportunityChangeLog(
            opportunity_id=opp_id,
            field_changed=field,
            old_value=old_val,
            new_value=new_val,
            source_id=source_id
        )
        # Session.add(log)
        pass

    def _snapshot_version(self, opp_id: int, old_data: Dict[str, Any]):
        """Engine 13: Full Version Snapshotting."""
        ver = OpportunityVersion(
            opportunity_id=opp_id,
            version_number=2, # Mock increment
            snapshot_data=old_data
        )
        # Session.add(ver)
        pass

    def _map_source(self, opp_id: int, source_id: int):
        """Engine 4: Source Aggregation Mapping."""
        mapping = OpportunitySourceMap(
            opportunity_id=opp_id,
            source_id=source_id
        )
        # Session.add(mapping)
        pass
