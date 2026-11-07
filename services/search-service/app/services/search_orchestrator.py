from typing import Any, Dict, List, Tuple

from app.schemas.search import SearchQueryRequest
from app.services.fuzzy_search import FuzzySearchEngine
from app.services.hybrid_search import HybridSearchEngine
from app.services.index_manager import IndexManager, SearchFilters
from app.services.keyword_search import KeywordSearchEngine
from app.services.semantic_search import SemanticSearchEngine


def run_search(manager: IndexManager, payload: SearchQueryRequest) -> Tuple[str, List[Dict[str, Any]], int]:
    """Run one search against a single consistent snapshot; returns (mode label, results, index version)."""
    snapshot = manager.snapshot
    filters = SearchFilters(
        city=payload.city,
        min_price=payload.min_price,
        max_price=payload.max_price,
        bedrooms=payload.bedrooms,
    )
    query = payload.query.strip()

    if not query:
        browse = [doc for doc in snapshot.docs.values() if filters.matches(doc)]
        browse.sort(key=lambda d: d.get("updated_at") or "", reverse=True)
        results = [dict(doc, score=0.0) for doc in browse]
        return "browse", results[:payload.limit], snapshot.version

    if payload.mode == "keyword":
        candidates = [doc for doc in snapshot.docs.values() if filters.matches(doc)]
        return "keyword", KeywordSearchEngine.search(query, candidates)[:payload.limit], snapshot.version

    if payload.mode == "fuzzy":
        results = FuzzySearchEngine.search(manager, snapshot, query, payload.limit, filters)
        return "fuzzy_trigram", results, snapshot.version

    if payload.mode == "semantic":
        results = SemanticSearchEngine.search(manager, snapshot, query, payload.limit, filters)
        return "semantic_faiss", results, snapshot.version

    results = HybridSearchEngine.hybrid_search(manager, snapshot, query, filters, payload.limit)
    return "hybrid_rrf", results[:payload.limit], snapshot.version
