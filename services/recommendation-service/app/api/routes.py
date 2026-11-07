import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import current_user_id
from app.repositories.recommendation_repository import RecommendationRepository, RepositoryError
from app.schemas.recommendation import RecommendationResponse
from app.schemas.roommate import RoommateCompatibilityRequest, RoommateCompatibilityResponse
from app.services.compatibility_engine import CompatibilityEngineService
from app.services.recommendation_engine import RecommendationEngineService

logger = logging.getLogger(__name__)

router = APIRouter()
comp_engine = CompatibilityEngineService()


def get_repository() -> RecommendationRepository:
    return RecommendationRepository()


@router.get("/listings/{user_id}", response_model=RecommendationResponse)
def get_user_recommendations(user_id: str, limit: int = Query(20, ge=1, le=50),
                             caller: str = Depends(current_user_id),
                             repository=Depends(get_repository)):
    try:
        requested = str(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Unknown user")
    if requested != caller:
        # Recommendations are derived from a person's activity, so they are only for that person.
        raise HTTPException(status_code=403, detail="You can only see your own recommendations")
    try:
        recs = RecommendationEngineService(repository).get_recommendations_for_user(caller, limit)
    except RepositoryError as exc:
        logger.error("Recommendations unavailable: %s", exc)
        raise HTTPException(status_code=503, detail="Recommendations are temporarily unavailable")
    return RecommendationResponse(user_id=caller, recommendations=recs)


@router.post("/roommate-compatibility", response_model=RoommateCompatibilityResponse)
def compute_roommate_compatibility(payload: RoommateCompatibilityRequest):
    score, summary = comp_engine.evaluate_pair(payload)
    return RoommateCompatibilityResponse(compatibility_score=score, summary=summary)


@router.get("/health")
def router_health():
    return {"status": "healthy", "service": "recommendation-service"}
