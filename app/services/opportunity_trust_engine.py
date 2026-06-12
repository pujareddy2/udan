from typing import Dict, Any, Tuple
from pydantic import BaseModel
from urllib.parse import urlparse

class TrustResult(BaseModel):
    trust_score: float
    trust_level: str
    source_type: str
    verified: bool

class OpportunityTrustEngine:
    """
    STAGE 14A: Opportunity Trust Engine
    Validates the source authority of discovered URLs.
    """

    def evaluate_trust(self, url: str) -> TrustResult:
        if not url:
            return TrustResult(trust_score=0, trust_level="Reject", source_type="Unknown", verified=False)
            
        domain = self._extract_domain(url)
        score, source_type = self._score_domain(domain)
        
        # Determine Level
        if score >= 95:
            level = "Verified"
        elif score >= 85:
            level = "Highly Trusted"
        elif score >= 70:
            level = "Trusted"
        elif score >= 50:
            level = "Needs Manual Review"
        else:
            level = "Reject"
            
        return TrustResult(
            trust_score=score,
            trust_level=level,
            source_type=source_type,
            verified=(score >= 95)
        )

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url if "://" in url else f"http://{url}")
            return parsed.netloc.lower()
        except:
            return ""

    def _score_domain(self, domain: str) -> Tuple[float, str]:
        if domain.endswith(".gov.in") or domain.endswith(".nic.in"):
            return 100.0, "Government Domain"
            
        if "scholarships.gov.in" in domain or "myscheme.gov.in" in domain:
            return 98.0, "Official National Portal"
            
        if domain.endswith(".edu.in") or domain.endswith(".ac.in"):
            return 90.0, "Recognized Educational Institution"
            
        if domain.endswith(".org.in") or domain.endswith(".org"):
            return 80.0, "Recognized NGO"
            
        # Basic heuristic for news/blogs (in reality, requires a known DB)
        if "news" in domain or "times" in domain:
            return 60.0, "News Portal"
            
        if "blog" in domain:
            return 20.0, "Blog"
            
        return 50.0, "Unknown Source" # Defaults to manual review if unsure but valid URL
