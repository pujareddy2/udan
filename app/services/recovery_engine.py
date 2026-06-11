from typing import Dict, Any, List
from app.services.eligibility import get_field, safe_float, safe_list

def match_recovery_opportunities(missed_opp: Dict[str, Any], active_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Searches for substitute opportunities and future cycles for a missed opportunity.
    """
    missed_title = missed_opp.get("opportunity_name", "")
    missed_module = missed_opp.get("module", "")
    missed_value = safe_float(missed_opp.get("benefit_value", 0.0))
    
    similar_active = []
    future_cycles = []
    state_alternatives = []
    private_alternatives = []
    
    total_recoverable = 0.0
    
    for opp in active_opportunities:
        title = get_field(opp, 'title', '')
        if title == missed_title:
            continue
            
        module = get_field(opp, 'module', '')
        val = safe_float(get_field(opp, 'benefit_amount', 0.0))
        provider_type = get_field(opp, 'provider_type', 'government').lower()
        scope = get_field(opp, 'geographic_scope', 'central').lower()
        
        # Determine Match Logic
        is_module_match = (module.lower() == missed_module.lower())
        
        if is_module_match:
            # 1. State Alternatives
            if scope == 'state':
                state_alternatives.append(title)
                similar_active.append({
                    "title": title,
                    "value": val,
                    "match_reason": "State-level alternative for the missed opportunity."
                })
                total_recoverable += val
                
            # 2. Private Alternatives
            elif provider_type == 'private':
                private_alternatives.append(title)
                similar_active.append({
                    "title": title,
                    "value": val,
                    "match_reason": "Private sector alternative."
                })
                total_recoverable += val
                
            # 3. Same Scheme Future Cycle (Mock detection logic)
            elif "2026" in title or "2027" in title:
                if missed_title.split()[0] in title: # Basic similarity check
                    future_cycles.append(f"{title} (Upcoming Cycle)")

    # Deduplicate
    state_alternatives = list(set(state_alternatives))
    private_alternatives = list(set(private_alternatives))
    future_cycles = list(set(future_cycles))
    
    return {
        "missed_opportunity": missed_title,
        "estimated_recoverable_value": total_recoverable,
        "similar_active_opportunities": similar_active,
        "future_cycles": future_cycles,
        "state_specific_alternatives": state_alternatives,
        "private_alternatives": private_alternatives
    }
