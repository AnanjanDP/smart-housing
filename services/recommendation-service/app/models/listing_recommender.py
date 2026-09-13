from typing import List, Dict, Any

class ListingRecommenderModel:
    def predict_top_listings(self, user_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "listing_id": "11111111-1111-1111-1111-111111111111",
                "title": "Luxury Studio in Downtown",
                "city": "San Francisco",
                "price": 2600.0,
                "recommendation_score": 96.5
            },
            {
                "listing_id": "22222222-2222-2222-2222-222222222222",
                "title": "Cozy 2BR Flat near Park",
                "city": "Palo Alto",
                "price": 3400.0,
                "recommendation_score": 88.0
            }
        ]
