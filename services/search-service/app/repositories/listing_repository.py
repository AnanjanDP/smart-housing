import os
import logging
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ListingRepository:
    _pool = None

    def __init__(self):
        self.db_name = os.getenv('POSTGRES_DB', 'staymatch_db')
        self.db_user = os.getenv('POSTGRES_USER', 'staymatch_user')
        self.db_password = os.getenv('POSTGRES_PASSWORD', 'staymatch_password')
        self.db_host = os.getenv('POSTGRES_HOST', 'postgres')
        self.db_port = os.getenv('POSTGRES_PORT', '5432')
        self._init_pool()

    def _init_pool(self):
        if ListingRepository._pool is None:
            try:
                ListingRepository._pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    host=self.db_host,
                    port=self.db_port,
                    connect_timeout=3
                )
                logger.info("ListingRepository PostgreSQL connection pool initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize PostgreSQL pool in search service: {e}")
                ListingRepository._pool = None

    def fetch_all_active_listings(self) -> List[Dict[str, Any]]:
        conn = None
        if ListingRepository._pool:
            try:
                conn = ListingRepository._pool.getconn()
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cursor.execute(
                    "SELECT id::text, title, description, city, state, price, bedrooms, is_available "
                    "FROM listings_listing WHERE is_available = True;"
                )
                rows = cursor.fetchall()
                cursor.close()
                ListingRepository._pool.putconn(conn)
                
                if rows:
                    results = []
                    for row in rows:
                        row_dict = dict(row)
                        row_dict['price'] = float(row_dict['price'])
                        results.append(row_dict)
                    return results
            except Exception as e:
                logger.error(f"Error executing query via connection pool: {e}")
                if conn and ListingRepository._pool:
                    try:
                        ListingRepository._pool.putconn(conn, close=True)
                    except Exception:
                        pass
                ListingRepository._pool = None

        # Return empty list if database returns no active listings or on connection error
        return []


