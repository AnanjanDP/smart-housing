import logging
from typing import Any, Dict, List, Optional

from app.services.index_manager import IndexManager, SearchFilters
from app.services.keyword_search import KeywordSearchEngine
from app.services.vector_index import IndexSnapshot

logger = logging.getLogger(__name__)


class FuzzySearchEngine:
    """Typo-tolerant ranking from PostgreSQL trigram similarity, restricted to the current index snapshot."""

    @staticmethod
    def search(manager: IndexManager, snapshot: IndexSnapshot, query: str, limit: int,
               filters: Optional[SearchFilters] = None) -> List[Dict[str, Any]]:
        fuzzy = getattr(manager.repository, "fuzzy_search", None)
        terms = KeywordSearchEngine.query_terms(query)
        if fuzzy is None or not terms:
            return []
        try:
            # Over-fetch: rows are dropped below if they are outside the snapshot or the filters.
            matches = fuzzy(terms, limit=max(limit * 3, 50))
        except Exception as exc:
            # The semantic and keyword legs still work, so a trigram failure should not fail the search.
            logger.warning("Fuzzy (trigram) search unavailable: %s", exc)
            return []
        results = []
        for match in matches:
            doc = snapshot.docs.get(match["id"])
            if doc is None or (filters is not None and not filters.matches(doc)):
                continue
            results.append(dict(doc, score=round(match["score"], 4)))
            if len(results) >= limit:
                break
        return results
