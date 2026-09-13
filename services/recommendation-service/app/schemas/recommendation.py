from pydantic import BaseModel
from typing import List

class RecommendationItem(BaseModel):
    listing_id: str
    title: str
    city: str
    price: float
    recommendation_score: float

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
