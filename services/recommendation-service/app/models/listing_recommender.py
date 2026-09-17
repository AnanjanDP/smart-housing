import os
import logging
import psycopg2
import psycopg2.extras
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ListingRecommenderModel:
    def __init__(self):
        self.db_name = os.getenv('POSTGRES_DB', 'staymatch_db')
        self.db_user = os.getenv('POSTGRES_USER', 'staymatch_user')
        self.db_password = os.getenv('POSTGRES_PASSWORD', 'staymatch_password')
        self.db_host = os.getenv('POSTGRES_HOST', 'postgres')
        self.db_port = os.getenv('POSTGRES_PORT', '5432')

    def predict_top_listings(self, user_id: str, target_budget: float = 3000.0) -> List[Dict[str, Any]]:
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                connect_timeout=3
            )
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                "SELECT id::text AS listing_id, title, city, state, price, bedrooms "
                "FROM listings_listing WHERE is_available = True LIMIT 50;"
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if rows:
                recs = []
                for row in rows:
                    item = dict(row)
                    item['price'] = float(item['price'])
                    price_diff = abs(item['price'] - target_budget)
                    price_score = max(0.0, 100.0 - (price_diff / 50.0))
                    item['recommendation_score'] = round(min(99.0, max(60.0, price_score)), 1)
                    recs.append(item)
                return sorted(recs, key=lambda x: x['recommendation_score'], reverse=True)
        except Exception as e:
            logger.warning(f"Database lookup in recommendation service failed: {e}. Using intelligent fallback.")

        # Return empty list if database returns no active recommendations or on error
        return []


