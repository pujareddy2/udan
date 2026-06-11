from typing import Dict, Any, List

def process_life_journey_timeline(timeline_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Processes raw timeline events into a Life Journey Dashboard and Impact Analytics.
    Expects events with: date, event_type, title, impact_value, description.
    """
    # Event Types: OPPORTUNITY_APPROVED, OPPORTUNITY_MISSED, OPPORTUNITY_RECOVERED, 
    # PROFILE_UPDATED, DOCUMENT_UPLOADED, NEW_OPPORTUNITY_UNLOCKED
    
    total_received = 0.0
    total_missed = 0.0
    total_recovered = 0.0
    
    successful_apps = 0
    total_apps = 0
    
    for event in timeline_events:
        evt_type = event.get('event_type', '')
        val = float(event.get('impact_value', 0.0))
        
        if evt_type == 'OPPORTUNITY_APPROVED':
            total_received += val
            successful_apps += 1
            total_apps += 1
        elif evt_type == 'OPPORTUNITY_MISSED':
            total_missed += val
        elif evt_type == 'OPPORTUNITY_RECOVERED':
            total_recovered += val
            successful_apps += 1
            total_apps += 1
        elif evt_type == 'APPLICATION_SUBMITTED' or evt_type == 'OPPORTUNITY_REJECTED':
            total_apps += 1
            
    success_rate = "0%"
    if total_apps > 0:
        success_rate = f"{int((successful_apps / total_apps) * 100)}%"

    # Sort events by date descending
    sorted_events = sorted(timeline_events, key=lambda x: x.get('date', ''), reverse=True)

    return {
        "impact_analytics": {
            "total_value_received": total_received,
            "total_value_missed": total_missed,
            "total_value_recovered": total_recovered,
            "application_success_rate": success_rate,
            "readiness_growth": "+N/A" # Would require historical snapshot data to calculate
        },
        "life_journey": sorted_events
    }
