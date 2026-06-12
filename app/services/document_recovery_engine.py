from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class RecoveryImpact(BaseModel):
    opportunities_blocked: int
    potential_value_blocked: float
    readiness_loss: float

class RecoveryDetails(BaseModel):
    difficulty: str
    processing_time: str
    apply_link: str
    state_authority: str

class RecoveryRoadmap(BaseModel):
    document_name: str
    importance: str
    impact: RecoveryImpact
    recovery_details: RecoveryDetails
    supporting_documents_required: List[str]
    steps: List[str]
    substitutes_available: List[str]

# ==========================================
# 2. DOCUMENT RECOVERY ENGINE
# ==========================================
class DocumentRecoveryEngine:
    """
    STAGE 13: Document Recovery Engine
    Converts missing documents into highly structured, state-localized Acquisition Roadmaps.
    """
    
    def __init__(self):
        # Mock State Processes Database
        self.state_db = {
            "Income Certificate": {
                "Telangana": {
                    "apply_link": "https://ts.meeseva.telangana.gov.in/",
                    "authority_name": "Revenue Department, Govt of Telangana",
                    "steps": [
                        "Step 1: Go to the MeeSeva Portal and register.",
                        "Step 2: Fill the Income Certificate Application form.",
                        "Step 3: Upload Aadhaar and Ration Card.",
                        "Step 4: Pay the ₹45 processing fee online.",
                        "Step 5: Wait for digital signature approval."
                    ],
                    "supporting_docs": ["Aadhaar", "Ration Card", "Passport Photo"]
                },
                "Maharashtra": {
                    "apply_link": "https://aaplesarkar.mahaonline.gov.in/",
                    "authority_name": "Revenue Department, Govt of Maharashtra",
                    "steps": [
                        "Step 1: Register on Aaple Sarkar portal.",
                        "Step 2: Apply for Income Certificate under Revenue Dept.",
                        "Step 3: Pay the ₹33 processing fee online."
                    ],
                    "supporting_docs": ["Aadhaar", "Address Proof", "Age Proof"]
                }
            }
        }
        
        # Mock Substitute Database
        self.substitutes_db = {
            "Address Proof": ["Aadhaar", "Voter ID", "Passport"],
            "Residence Certificate": ["Aadhaar", "Voter ID", "Ration Card"]
        }

    def generate_recovery_roadmap(self, missing_document: str, user_state: str, user_wallet_docs: List[str], blocked_opportunities: List[Dict[str, Any]]) -> RecoveryRoadmap:
        """Main Orchestrator for generating the Recovery Roadmap JSON."""
        
        # 1. Substitute Check (Engine 14)
        substitutes = self._check_substitutes(missing_document, user_wallet_docs)
        if substitutes:
            return self._build_bypass_roadmap(missing_document, substitutes)
        
        # 2. Impact Analyzer (Engine 1)
        blocked_count = len(blocked_opportunities)
        blocked_value = sum(opp.get("financial_value", 0.0) for opp in blocked_opportunities)
        
        # 3. Priority Engine (Engine 2)
        importance = self._calculate_priority(blocked_count, blocked_value)
        
        # 4. State Specific Routing (Engine 8)
        state_data = self._get_state_process(missing_document, user_state)
        
        # 5. Timeline & Difficulty (Engines 6 & 7)
        difficulty = "Medium" # Default mock
        time = "7-14 Days" # Default mock
        
        return RecoveryRoadmap(
            document_name=missing_document,
            importance=importance,
            impact=RecoveryImpact(
                opportunities_blocked=blocked_count,
                potential_value_blocked=blocked_value,
                readiness_loss=15.0 # Standard mock deduction
            ),
            recovery_details=RecoveryDetails(
                difficulty=difficulty,
                processing_time=time,
                apply_link=state_data.get("apply_link", "Contact Local CSC Center"),
                state_authority=state_data.get("authority_name", "Local Revenue Authority")
            ),
            supporting_documents_required=state_data.get("supporting_docs", ["Aadhaar"]),
            steps=state_data.get("steps", ["Step 1: Visit your nearest Common Service Center (CSC)."]),
            substitutes_available=[]
        )

    # --- ENGINES ---

    def _check_substitutes(self, document_name: str, wallet: List[str]) -> List[str]:
        """Engine 14: Bypasses recovery if a valid substitute is already in the wallet."""
        valid_subs = self.substitutes_db.get(document_name, [])
        found_subs = []
        wallet_lower = [d.lower() for d in wallet]
        
        for sub in valid_subs:
            if sub.lower() in wallet_lower:
                found_subs.append(sub)
                
        return found_subs

    def _calculate_priority(self, blocked_count: int, blocked_value: float) -> str:
        """Engine 2: Scientific financial classification."""
        if blocked_count >= 10 or blocked_value >= 100000:
            return "Critical"
        elif blocked_count >= 5:
            return "High"
        elif blocked_count >= 2:
            return "Medium"
        return "Low"

    def _get_state_process(self, document_name: str, state: str) -> Dict[str, Any]:
        """Engine 8: Localized URL and Rules fetching."""
        doc_data = self.state_db.get(document_name, {})
        # Try specific state, fallback to empty dict
        return doc_data.get(state, {})

    def _build_bypass_roadmap(self, document_name: str, substitutes: List[str]) -> RecoveryRoadmap:
        """Special Output if a substitute is found."""
        return RecoveryRoadmap(
            document_name=document_name,
            importance="Resolved",
            impact=RecoveryImpact(opportunities_blocked=0, potential_value_blocked=0.0, readiness_loss=0.0),
            recovery_details=RecoveryDetails(
                difficulty="Bypassed",
                processing_time="Instant",
                apply_link="",
                state_authority=""
            ),
            supporting_documents_required=[],
            steps=[f"You don't need to apply! The system has automatically used your {substitutes[0]} as a valid substitute."],
            substitutes_available=substitutes
        )
