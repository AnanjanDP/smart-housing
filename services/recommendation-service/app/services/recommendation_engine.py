from app.models.listing_recommender import ListingRecommenderModel


class RecommendationEngineService:
    def __init__(self, repository, model: ListingRecommenderModel = None):
        self.repository = repository
        self.model = model or ListingRecommenderModel()

    def get_recommendations_for_user(self, user_id: str, limit: int = 20):
        candidates = self.repository.fetch_candidates(user_id)
        if not candidates:
            return []
        return self.model.recommend(
            candidates=candidates,
            interactions=self.repository.fetch_interactions(user_id),
            profile=self.repository.fetch_profile(user_id),
            limit=limit,
        )
