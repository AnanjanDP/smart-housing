from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchQueryRequest(BaseModel):
    query: str
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    limit: int = 20

class SearchResultItem(BaseModel):
    id: str
    title: str
    description: str
    city: str
    price: float
    bedrooms: int
    score: float

class SearchResponse(BaseModel):
    total: int
    mode: str
    results: List[SearchResultItem]
