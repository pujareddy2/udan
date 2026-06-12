import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.profile_context import SearchContextObject

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class RankedQuery(BaseModel):
    query_string: str
    query_type: str
    target_category: str
    intent_score: float
    discovery_score: float
    relevance_score: float
    gov_confidence_score: float
    freshness_score: float
    final_score: float
    search_frequency: str
    search_depth: str
    source_targets: List[str]

class SearchStrategyObject(BaseModel):
    user_id: str
    high_priority_queries: List[RankedQuery]
    medium_priority_queries: List[RankedQuery]
    low_priority_queries: List[RankedQuery]
    total_queries_generated: int

# ==========================================
# 2. SOURCE TARGETING MAPPINGS
# ==========================================
CATEGORY_SOURCE_MAP = {
    "Scholarships": ["site:scholarships.gov.in", "site:edu.in"],
    "Subsidies": ["site:agricoop.nic.in", "site:*.gov.in"],
    "PM Kisan": ["site:pmkisan.gov.in"],
    "Crop Insurance": ["site:pmfby.gov.in"],
    "Jobs": ["site:ncs.gov.in", "site:*.nic.in"],
    "Startups": ["site:startupindia.gov.in", "site:msme.gov.in"],
    "MSME": ["site:msme.gov.in", "site:udyamregistration.gov.in"],
    "General": ["site:gov.in", "site:nic.in"]
}

# ==========================================
# 3. QUERY GENERATOR AGENT
# ==========================================
class QueryGenerationAgent:
    """
    STAGE 4: Internet Discovery Query Strategy
    Translates mathematical profile context into an army of Serper API queries.
    """
    
    def generate_search_strategy(self, context: SearchContextObject) -> SearchStrategyObject:
        # Step 1: Call LLM for base queries
        raw_queries = self._call_gemini_api(context)
        
        # Fallback if Gemini hallucinates
        if not raw_queries:
            raw_queries = self._fallback_queries(context)
            
        ranked_queries = []
        
        for rq in raw_queries:
            # Step 2: Scoring
            scored_q = self._rank_queries(rq, context)
            
            # Step 3: Attach Domains
            scored_q = self._attach_sources(scored_q)
            
            # Step 4: Frequency & Depth
            scored_q = self._assign_frequency_and_depth(scored_q)
            
            ranked_queries.append(scored_q)
            
        # Step 5: Bucketizing
        high = [q for q in ranked_queries if q.search_frequency == "Daily"]
        medium = [q for q in ranked_queries if q.search_frequency == "Weekly"]
        low = [q for q in ranked_queries if q.search_frequency == "Monthly"]
        
        return SearchStrategyObject(
            user_id=context.user_id,
            high_priority_queries=high,
            medium_priority_queries=medium,
            low_priority_queries=low,
            total_queries_generated=len(ranked_queries)
        )

    def _call_gemini_api(self, context: SearchContextObject) -> List[Dict[str, Any]]:
        """
        In production, executes the Few-Shot Prompt via the google-genai library.
        Returns a strict JSON list of 50 queries.
        """
        system_prompt = f"""
        You are an expert Government Opportunity Researcher. Generate exactly 50 specialized search engine queries designed to uncover government schemes, subsidies, jobs, and grants.
        Your queries must cover 6 Types: Exact Match, Eligibility, Benefit, Opportunity Discovery, Regional, and Hidden Opportunity.
        
        USER CONTEXT:
        Personas: {context.personas}
        Priority Categories: {context.priority_categories}
        Base Keywords: {context.search_keywords}
        """
        
        # Mocking 3 queries for architectural execution simulation
        return [
            {
                "query_string": f"Government {context.priority_categories[0] if context.priority_categories else 'schemes'} for {context.personas[0]} 2026",
                "query_type": "Type 1",
                "target_category": context.priority_categories[0] if context.priority_categories else "General",
                "intent_score": 0.9,
                "discovery_score": 0.2
            },
            {
                "query_string": "Eligibility for financial subsidy scheme details",
                "query_type": "Type 2",
                "target_category": "Subsidies",
                "intent_score": 0.7,
                "discovery_score": 0.5
            },
            {
                "query_string": "Hidden undiscovered state grants 2026",
                "query_type": "Type 6",
                "target_category": "General",
                "intent_score": 0.4,
                "discovery_score": 0.9
            }
        ]

    def _fallback_queries(self, context: SearchContextObject) -> List[Dict[str, Any]]:
        """Static fallback if LLM times out or hallucinates."""
        fallback = []
        for kw in context.search_keywords.get("primary", []):
            fallback.append({
                "query_string": kw,
                "query_type": "Type 1",
                "target_category": "General",
                "intent_score": 1.0,
                "discovery_score": 0.0
            })
        return fallback

    def _rank_queries(self, raw_query: Dict[str, Any], context: SearchContextObject) -> RankedQuery:
        """Math engine to determine exact value of a query before burning Serper API credits."""
        
        q_str = raw_query.get("query_string", "").lower()
        intent_score = float(raw_query.get("intent_score", 0.0))
        discovery_score = float(raw_query.get("discovery_score", 0.0))
        
        # Relevance
        relevance_score = 0.5
        for cat in context.priority_categories:
            if cat.lower() in q_str:
                relevance_score = 0.9
                break
                
        # Gov Confidence
        gov_confidence_score = 0.0
        gov_keywords = ["government", "scheme", "subsidy", "yojana", "portal", "grant", "apply"]
        if any(g in q_str for g in gov_keywords):
            gov_confidence_score = 1.0
            
        # Freshness
        freshness_score = 1.0 if "2026" in q_str or "2025" in q_str else 0.0
        
        # Final Score Formula
        final_score = (intent_score * 0.3) + (relevance_score * 0.3) + (gov_confidence_score * 0.2) + (freshness_score * 0.1) + (discovery_score * 0.1)
        
        return RankedQuery(
            query_string=raw_query.get("query_string", ""),
            query_type=raw_query.get("query_type", "Type 1"),
            target_category=raw_query.get("target_category", "General"),
            intent_score=intent_score,
            discovery_score=discovery_score,
            relevance_score=relevance_score,
            gov_confidence_score=gov_confidence_score,
            freshness_score=freshness_score,
            final_score=round(final_score, 3),
            search_frequency="",
            search_depth="",
            source_targets=[]
        )

    def _attach_sources(self, query: RankedQuery) -> RankedQuery:
        """Injects site: modifiers to force Google/Serper to use authoritative domains."""
        targets = []
        for cat, domains in CATEGORY_SOURCE_MAP.items():
            if cat.lower() in query.target_category.lower() or cat.lower() in query.query_string.lower():
                targets.extend(domains)
        
        if not targets:
            targets = CATEGORY_SOURCE_MAP["General"]
            
        query.source_targets = list(set(targets))
        return query

    def _assign_frequency_and_depth(self, query: RankedQuery) -> RankedQuery:
        """Determines execution schedule based on Final Query Score."""
        
        if query.final_score > 0.8:
            query.search_frequency = "Daily"
            query.search_depth = "Level 1" # Just top 10 results, check for immediate news
        elif query.final_score > 0.5:
            query.search_frequency = "Weekly"
            query.search_depth = "Level 2" # Top 30 results + Gov Sources
        else:
            query.search_frequency = "Monthly"
            query.search_depth = "Level 3" # Deep pagination for hidden/discovery queries
            
        return query
