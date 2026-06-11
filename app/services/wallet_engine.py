from typing import Dict, Any, List

def categorize_opportunities(opps_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Categorizes a list of processed opportunity objects into Wallet Bins.
    Expects each opp object to contain:
    - eligible: bool
    - readiness_score: float
    - deadline_risk: str ('Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk')
    - days_remaining: int
    - benefit_value: float
    - title: str
    - blocking_items: list (optional)
    - blocking_reasons: list (optional)
    """
    wallet = {
        "available_now": {"opportunity_count": 0, "total_value": 0.0, "opportunities": []},
        "almost_ready": {"opportunity_count": 0, "unlock_value": 0.0, "blocking_items": set(), "opportunities": []},
        "blocked": {"opportunity_count": 0, "lost_value": 0.0, "blocking_reasons": set(), "opportunities": []},
        "expiring_soon": {"opportunity_count": 0, "value_at_risk": 0.0, "days_remaining": float('inf'), "opportunities": []},
        "missed": {"opportunity_count": 0, "missed_value": 0.0, "opportunities": []} # Missed handled separately if past deadline
    }
    
    for opp in opps_data:
        title = opp.get("title", "Unknown Scheme")
        val = float(opp.get("benefit_value", 0.0))
        eligible = opp.get("eligible", False)
        readiness = float(opp.get("readiness_score", 0.0))
        deadline_risk = opp.get("deadline_risk", "Low Risk")
        days_rem = opp.get("days_remaining", 365)
        missed_val = float(opp.get("missed_value", 0.0))
        
        # 1. Missed Bucket
        if missed_val > 0 and days_rem < 0:
            wallet["missed"]["opportunity_count"] += 1
            wallet["missed"]["missed_value"] += missed_val
            wallet["missed"]["opportunities"].append(title)
            continue
            
        # 2. Expiring Soon Bucket
        if days_rem <= 7 and deadline_risk in ["High Risk", "Critical Risk", "Medium Risk"]:
            wallet["expiring_soon"]["opportunity_count"] += 1
            wallet["expiring_soon"]["value_at_risk"] += val
            wallet["expiring_soon"]["days_remaining"] = min(wallet["expiring_soon"]["days_remaining"], days_rem)
            wallet["expiring_soon"]["opportunities"].append(title)
            
            # Note: We continue because an expiring opportunity can ALSO be "Almost Ready" or "Available Now"
            
        # 3. Blocked Bucket
        if not eligible:
            wallet["blocked"]["opportunity_count"] += 1
            wallet["blocked"]["lost_value"] += val
            wallet["blocked"]["opportunities"].append(title)
            for r in opp.get("blocking_reasons", []):
                wallet["blocked"]["blocking_reasons"].add(r)
            continue
            
        # 4. Available Now Bucket
        if readiness >= 90.0 and deadline_risk in ["Low Risk", "Medium Risk"]:
            wallet["available_now"]["opportunity_count"] += 1
            wallet["available_now"]["total_value"] += val
            wallet["available_now"]["opportunities"].append(title)
            continue
            
        # 5. Almost Ready Bucket
        if readiness < 90.0:
            wallet["almost_ready"]["opportunity_count"] += 1
            wallet["almost_ready"]["unlock_value"] += val
            wallet["almost_ready"]["opportunities"].append(title)
            for i in opp.get("blocking_items", []):
                wallet["almost_ready"]["blocking_items"].add(i)

    # Convert sets to lists for JSON serialization
    wallet["almost_ready"]["blocking_items"] = list(wallet["almost_ready"]["blocking_items"])
    wallet["blocked"]["blocking_reasons"] = list(wallet["blocked"]["blocking_reasons"])
    
    if wallet["expiring_soon"]["days_remaining"] == float('inf'):
        wallet["expiring_soon"]["days_remaining"] = None
        
    return wallet

def build_opportunity_wallet(opps_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    categories = categorize_opportunities(opps_data)
    
    summary = {
        "available_value": categories["available_now"]["total_value"],
        "unlockable_value": categories["almost_ready"]["unlock_value"],
        "blocked_value": categories["blocked"]["lost_value"],
        "expiring_value": categories["expiring_soon"]["value_at_risk"],
        "missed_value": categories["missed"]["missed_value"],
        "total_opportunity_value": categories["available_now"]["total_value"] + categories["almost_ready"]["unlock_value"]
    }
    
    return {
        "wallet_summary": summary,
        "categories": categories
    }
