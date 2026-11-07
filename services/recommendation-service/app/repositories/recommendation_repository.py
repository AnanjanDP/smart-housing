import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

CANDIDATE_LIMIT = 500
INTERACTION_LIMIT = 200

LISTING_COLUMNS = "l.id::text AS id, l.title, l.city, l.state, l.price, l.bedrooms, l.bathrooms, l.amenities"


class RepositoryError(Exception):
    """The database could not be read."""


class RecommendationRepository:
    """Read-only access to the data recommendations are built from."""

    def __init__(self):
        self.params = dict(
            dbname=os.getenv('POSTGRES_DB', 'staymatch_db'),
            user=os.getenv('POSTGRES_USER', 'staymatch_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'staymatch_password'),
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            connect_timeout=3,
        )

    @contextmanager
    def _cursor(self):
        try:
            conn = psycopg2.connect(**self.params)
        except psycopg2.Error as exc:
            raise RepositoryError(f"database unavailable: {exc}") from exc
        try:
            conn.set_session(readonly=True)
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                yield cursor
        except psycopg2.Error as exc:
            raise RepositoryError(f"query failed: {exc}") from exc
        finally:
            conn.close()

    def fetch_candidates(self, user_id: str) -> List[Dict[str, Any]]:
        """Available listings the user does not own, newest first."""
        with self._cursor() as cursor:
            cursor.execute(
                f"SELECT {LISTING_COLUMNS} FROM listings_listing l "
                "WHERE l.is_available = TRUE AND l.owner_id <> %s::uuid "
                "ORDER BY l.created_at DESC LIMIT %s",
                (user_id, CANDIDATE_LIMIT),
            )
            return [dict(row) for row in cursor.fetchall()]

    def fetch_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        with self._cursor() as cursor:
            cursor.execute(
                f"SELECT i.action, {LISTING_COLUMNS} FROM interactions_interaction i "
                "JOIN listings_listing l ON l.id = i.listing_id "
                "WHERE i.user_id = %s::uuid ORDER BY i.timestamp DESC LIMIT %s",
                (user_id, INTERACTION_LIMIT),
            )
            rows = cursor.fetchall()
        return [{"action": row["action"], "listing": {k: v for k, v in row.items() if k != "action"}} for row in rows]

    def fetch_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT budget_min, budget_max, preferred_location FROM roommates_roommateprofile "
                "WHERE user_id = %s::uuid",
                (user_id,),
            )
            row = cursor.fetchone()
        return dict(row) if row else None
