from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class SearchQueryRequest(BaseModel):
    query: str = ""
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    mode: Literal["hybrid", "semantic", "keyword", "fuzzy"] = "hybrid"
    limit: int = Field(default=20, ge=1, le=100)

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
    index_version: int = 0
    results: List[SearchResultItem]
