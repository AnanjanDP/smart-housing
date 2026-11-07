from typing import List, Dict, Any, Optional

from app.services.index_manager import IndexManager, SearchFilters
from app.services.keyword_search import KeywordSearchEngine
from app.services.semantic_search import SemanticSearchEngine
from app.services.vector_index import IndexSnapshot

RRF_K = 60


class HybridSearchEngine:
    @staticmethod
    def fuse(rankings: List[List[Dict[str, Any]]], k: int = RRF_K) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion: each list contributes 1 / (k + rank) for every listing it ranks.

        Only ranks are used, so keyword scores and cosine similarities (which are not comparable) can
        be combined without normalisation.
        """
        scores: Dict[str, float] = {}
        docs: Dict[str, Dict[str, Any]] = {}
        for ranking in rankings:
            for rank, item in enumerate(ranking, start=1):
                scores[item['id']] = scores.get(item['id'], 0.0) + 1.0 / (k + rank)
                docs.setdefault(item['id'], item)

        merged = []
        for item_id, rrf_value in scores.items():
            result = docs[item_id].copy()
            result['score'] = round(rrf_value * 100, 3)
            merged.append(result)
        return sorted(merged, key=lambda x: (-x['score'], x['id']))

    @staticmethod
    def hybrid_search(
        manager: IndexManager,
        snapshot: IndexSnapshot,
        query: str,
        filters: Optional[SearchFilters],
        limit: int,
        pool: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        pool = pool or max(limit * 5, 50)
        candidates = [
            doc for doc in snapshot.docs.values() if filters is None or filters.matches(doc)
        ]
        keyword = KeywordSearchEngine.search(query, candidates)[:pool]
        semantic = SemanticSearchEngine.search(manager, snapshot, query, pool, filters)
        return HybridSearchEngine.fuse([keyword, semantic])
