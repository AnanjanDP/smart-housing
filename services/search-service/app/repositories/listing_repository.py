from typing import List, Dict, Any

class ListingRepository:
    def fetch_all_active_listings(self) -> List[Dict[str, Any]]:
        # Mock database fetcher for search service isolation
        return [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "title": "Luxury Studio in Downtown",
                "description": "Modern sunny studio apartment with gym and pool.",
                "city": "San Francisco",
                "price": 2600.0,
                "bedrooms": 1
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "title": "Cozy 2BR Flat near Park",
                "description": "Spacious flat close to transit and quiet neighborhood.",
                "city": "Palo Alto",
                "price": 3400.0,
                "bedrooms": 2
            }
        ]
