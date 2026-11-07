from typing import Any, Dict, List, Optional

from app.services.index_manager import IndexManager, SearchFilters
from app.services.vector_index import IndexSnapshot


class SemanticSearchEngine:
    """Embedding search over the FAISS index: cosine similarity between query and listing vectors."""

    @staticmethod
    def search(
        manager: IndexManager,
        snapshot: IndexSnapshot,
        query: str,
        limit: int,
        filters: Optional[SearchFilters] = None,
    ) -> List[Dict[str, Any]]:
        hits = manager.semantic_search(query, limit, filters, snapshot=snapshot)
        results = []
        for listing_id, score in hits:
            item = snapshot.docs[listing_id].copy()
            item["score"] = round(score, 4)
            results.append(item)
        return results
