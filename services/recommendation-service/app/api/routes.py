from fastapi import APIRouter
from app.schemas.recommendation import RecommendationResponse
from app.schemas.roommate import RoommateCompatibilityRequest, RoommateCompatibilityResponse
from app.services.recommendation_engine import RecommendationEngineService
from app.services.compatibility_engine import CompatibilityEngineService

router = APIRouter()
rec_engine = RecommendationEngineService()
comp_engine = CompatibilityEngineService()

@router.get("/listings/{user_id}", response_model=RecommendationResponse)
def get_user_recommendations(user_id: str):
    recs = rec_engine.get_recommendations_for_user(user_id)
    return RecommendationResponse(user_id=user_id, recommendations=recs)

@router.post("/roommate-compatibility", response_model=RoommateCompatibilityResponse)
def compute_roommate_compatibility(payload: RoommateCompatibilityRequest):
    score, summary = comp_engine.evaluate_pair(payload)
    return RoommateCompatibilityResponse(compatibility_score=score, summary=summary)

@router.get("/health")
def router_health():
    return {"status": "healthy", "service": "recommendation-service"}

