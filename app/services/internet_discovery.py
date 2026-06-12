import re
import hashlib
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pydantic import BaseModel
from app.services.query_generator import SearchStrategyObject, RankedQuery
from app.models.discovery import OpportunitySource, DiscoveredOpportunity, OpportunitySearchHistory

# ==========================================
# 1. OUTPUT SCHEMAS
# ==========================================
class DiscoveredSourceResult(BaseModel):
    source_url: str
    title: str
    domain: str
    source_type: str
    trust_score: float
    module_type: str
    query_used: str
    target_category: str

# ==========================================
# 2. FILTERING AND SCORING CONSTANTS
# ==========================================
REJECT_DOMAINS = [
    "youtube.com", "facebook.com", "instagram.com", "twitter.com", "quora.com", "reddit.com",
    "sarkariresult", "freejobalert", "bankersadda", "timesofindia", "ndtv.com", "livemint.com", "thehindu.com",
    "wikipedia.org", "pinterest.com", "linkedin.com"
]

REJECT_EXTENSIONS = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".exe", ".rar"]

# ==========================================
# 3. INTERNET DISCOVERY AGENT
# ==========================================
class InternetDiscoveryAgent:
    """
    STAGE 5: Internet Discovery
    Executes Serper queries, filters junk, scores domains, and queues pure sources.
    """
    
    def execute_discovery(self, strategy: SearchStrategyObject) -> List[DiscoveredSourceResult]:
        discovered_results = []
        
        # Execute only High Priority for immediate queueing (Medium/Low run in background)
        for query in strategy.high_priority_queries:
            # Step 1: Serper API Call
            raw_results = self._call_serper_api(query)
            
            for result in raw_results:
                url = result.get("link", "")
                title = result.get("title", "")
                
                # Step 2: Canonicalize URL
                canonical_url = self._canonicalize_url(url)
                if not canonical_url:
                    continue
                    
                # Step 3: Source Filtering
                if not self._filter_sources(canonical_url):
                    continue
                    
                # Step 4: Trust Scoring
                domain = urlparse(canonical_url).netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                    
                trust_score = self._calculate_trust_score(domain)
                if trust_score < 60:
                    continue # Drop low trust sources entirely
                    
                # Step 5: Module Classification & Formatting
                # Module is carried over from the query context (assumed mapped via query's persona in higher scope, but we use target_category here)
                discovered = DiscoveredSourceResult(
                    source_url=canonical_url,
                    title=title,
                    domain=domain,
                    source_type="Serper API",
                    trust_score=trust_score,
                    module_type=self._classify_module(query),
                    query_used=query.query_string,
                    target_category=query.target_category
                )
                
                discovered_results.append(discovered)
                
        # (In a real system, here we would merge to Database using SQLModel)
        # self._store_and_queue_results(discovered_results)
                
        return discovered_results

    def _call_serper_api(self, query: RankedQuery) -> List[Dict[str, str]]:
        """
        Mock implementation of the Serper HTTPx call.
        Payload uses query.query_string and query.source_targets.
        """
        # Simulated Serper JSON response
        return [
            {"title": "Apply for PM Kisan Yojana 2026", "link": "https://pmkisan.gov.in/registration?lang=en&session=123"},
            {"title": "Top 10 Farmer Schemes (Blog)", "link": "https://sarkariresult.com/farmer-schemes-2026"},
            {"title": "State Subsidy Scheme Notification", "link": "https://agricoop.nic.in/subsidy/telangana-2026.pdf"},
            {"title": "Agriculture Equipment Grants", "link": "https://nabard.org/grants/equipment/"}
        ]

    def _canonicalize_url(self, url: str) -> str:
        """Strips UTMs and standardizes the URL to prevent duplicates."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return ""
                
            # Filter bad extensions early
            if any(parsed.path.lower().endswith(ext) for ext in REJECT_EXTENSIONS):
                return ""
                
            # Keep only safe query parameters if necessary, but generally strip utm_
            qs = parse_qs(parsed.query)
            clean_qs = {k: v for k, v in qs.items() if not k.lower().startswith("utm_") and k.lower() not in ["session", "lang"]}
            
            return urlunparse((
                "https", # Force HTTPS canonicalization for trust check
                parsed.netloc.lower(),
                parsed.path,
                parsed.params,
                urlencode(clean_qs, doseq=True),
                "" # Strip fragments
            ))
        except Exception:
            return ""

    def _filter_sources(self, url: str) -> bool:
        """Regex and list-based rejection of bad domains."""
        domain = urlparse(url).netloc.lower()
        
        # Check explicit reject list
        for bad_domain in REJECT_DOMAINS:
            if bad_domain in domain:
                return False
                
        return True

    def _calculate_trust_score(self, domain: str) -> float:
        """Mathematical priority scoring of TLDs."""
        score = 20.0 # Default unknown
        
        if domain.endswith(".gov.in") or domain.endswith(".nic.in") or domain == "india.gov.in":
            score = 100.0
        elif domain.endswith(".edu.in") or domain.endswith(".ac.in"):
            score = 90.0
        elif domain.endswith(".org") or domain.endswith(".org.in"):
            score = 80.0
            # Boost known government partners
            if "nabard" in domain or "nsdc" in domain or "aicte" in domain:
                score += 10.0
        elif domain.endswith(".com") or domain.endswith(".in"):
            score = 60.0
            
        return min(100.0, score)

    def _classify_module(self, query: RankedQuery) -> str:
        """Derives module type based on the query target category."""
        cat = query.target_category.lower()
        if "student" in cat or "scholarship" in cat: return "Student"
        if "farmer" in cat or "kisan" in cat or "crop" in cat: return "Farmer"
        if "job" in cat or "apprentice" in cat: return "Job Seeker"
        if "startup" in cat or "msme" in cat: return "Startup"
        if "women" in cat or "shg" in cat: return "Women Entrepreneur"
        if "senior" in cat or "pension" in cat: return "Senior Citizen"
        return "Entrepreneur" # Default fallback
