from app.models.listing_recommender import ListingRecommenderModel

class RecommendationEngineService:
    def __init__(self):
        self.model = ListingRecommenderModel()

    def get_recommendations_for_user(self, user_id: str):
        return self.model.predict_top_listings(user_id)
