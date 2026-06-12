from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/search", tags=["Search"])
def search_opportunities(req: SearchRequest):
    """Natural language search for schemes and opportunities."""
    return {
        "query": req.query,
        "results": [
            {
                "id": 1,
                "title": "NSP Post-Matric Scholarship",
                "match_score": 95
            }
        ]
    }
