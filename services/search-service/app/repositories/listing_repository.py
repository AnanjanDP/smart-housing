import os
import logging
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

LISTING_COLUMNS = "id::text, title, description, city, state, price, bedrooms, is_available, updated_at"


class ListingRepositoryError(RuntimeError):
    """Raised when listings cannot be read; callers must not treat this as "no listings"."""


def _row_to_listing(row) -> Dict[str, Any]:
    listing = dict(row)
    listing['price'] = float(listing['price'])
    updated_at = listing.get('updated_at')
    listing['updated_at'] = updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at or '')
    return listing


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

    @contextmanager
    def _cursor(self):
        """Yield a dict cursor from the pool; raise ListingRepositoryError on any failure.

        A failed connection is discarded and the pool is rebuilt on the next call, so one database
        outage does not disable the repository until the process restarts.
        """
        if ListingRepository._pool is None:
            self._init_pool()
        pool = ListingRepository._pool
        if pool is None:
            raise ListingRepositoryError("PostgreSQL is unavailable")

        conn = None
        try:
            conn = pool.getconn()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                yield cursor
            conn.rollback()
            pool.putconn(conn)
        except Exception as e:
            logger.error(f"Listing query failed: {e}")
            if conn is not None:
                try:
                    pool.putconn(conn, close=True)
                except Exception:
                    pass
            ListingRepository._pool = None
            raise ListingRepositoryError(str(e)) from e

    def fetch_listing_versions(self) -> Dict[str, str]:
        """Cheap scan used to detect changes: listing id -> updated_at for every available listing."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT id::text AS id, updated_at FROM listings_listing WHERE is_available = TRUE;"
            )
            return {
                row['id']: (row['updated_at'].isoformat() if hasattr(row['updated_at'], 'isoformat')
                            else str(row['updated_at'] or ''))
                for row in cursor.fetchall()
            }

    def fetch_listings_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        if not ids:
            return []
        with self._cursor() as cursor:
            cursor.execute(
                f"SELECT {LISTING_COLUMNS} FROM listings_listing "
                "WHERE is_available = TRUE AND id = ANY(%s::uuid[]);",
                (list(ids),),
            )
            return [_row_to_listing(row) for row in cursor.fetchall()]

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
