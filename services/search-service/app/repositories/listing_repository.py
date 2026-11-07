import os
import logging
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

LISTING_COLUMNS = "id::text, title, description, city, state, price, bedrooms, is_available, updated_at"


FUZZY_FIELDS = ("title", "city", "state", "address")
MAX_FUZZY_TERMS = 8


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

    def fetch_listing_owner(self, listing_id: str):
        """The owner's user id for a listing, or None if the listing does not exist."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT owner_id::text AS owner_id FROM listings_listing WHERE id = %s::uuid;",
                (listing_id,),
            )
            row = cursor.fetchone()
            return row["owner_id"] if row else None

    def fuzzy_search(self, terms: List[str], min_similarity: float = 0.45, limit: int = 100) -> List[Dict[str, Any]]:
        """Typo-tolerant search with PostgreSQL trigrams (pg_trgm).

        Each term is compared with the title, city, state and address using word_similarity, which scores the
        best-matching stretch of the text, so "banglore" finds "Bangalore" and "studo" finds "studio". A term
        counts when its best score reaches `min_similarity`; a listing's score is the mean over all terms, so
        listings matching more of the query rank higher. Returns [{"id", "score"}], best first.
        """
        terms = [t for t in terms if t][:MAX_FUZZY_TERMS]
        if not terms:
            return []
        best = "GREATEST(" + ", ".join(f"word_similarity(%s, {field})" for field in FUZZY_FIELDS) + ")"
        # `<%%` (a literal `<%` once psycopg2 has processed the placeholders) is the indexable word-similarity operator (it uses the GIN indexes on these columns).
        any_match = " OR ".join(f"%s <%% {field}" for field in FUZZY_FIELDS)
        score_terms = " + ".join(f"CASE WHEN {best} >= %s THEN {best} ELSE 0 END" for _ in terms)
        where_terms = " OR ".join(f"({any_match})" for _ in terms)

        # Placeholders are filled in the order they appear in the SQL text.
        score_params = []
        for term in terms:
            score_params += [term] * len(FUZZY_FIELDS) + [min_similarity] + [term] * len(FUZZY_FIELDS)
        where_params = []
        for term in terms:
            where_params += [term] * len(FUZZY_FIELDS)

        sql = (
            f"SELECT id::text AS id, ({score_terms}) / {len(terms)}.0 AS score FROM listings_listing "
            f"WHERE is_available = TRUE AND ({where_terms}) ORDER BY score DESC, id LIMIT %s;"
        )
        with self._cursor() as cursor:
            cursor.execute("SET LOCAL pg_trgm.word_similarity_threshold = %s;", (min_similarity,))
            cursor.execute(sql, score_params + where_params + [limit])
            return [{"id": row["id"], "score": float(row["score"])} for row in cursor.fetchall() if row["score"] > 0]
