from typing import List

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    listing_id: str
    title: str
    city: str
    state: str = ""
    price: float
    bedrooms: int = 0
    recommendation_score: float
    reasons: List[str] = []


class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
