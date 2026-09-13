from typing import List, Dict, Any
from app.services.keyword_search import KeywordSearchEngine
from app.services.semantic_search import SemanticSearchEngine

class HybridSearchEngine:
    @staticmethod
    def hybrid_search(query: str, listings: List[Dict[str, Any]], k: int = 60) -> List[Dict[str, Any]]:
        keyword_res = KeywordSearchEngine.search(query, listings)
        semantic_res = SemanticSearchEngine.vector_search(query, listings)
        
        # Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        for rank, item in enumerate(keyword_res):
            rrf_scores[item['id']] = rrf_scores.get(item['id'], 0.0) + (1.0 / (k + rank + 1))
            
        for rank, item in enumerate(semantic_res):
            rrf_scores[item['id']] = rrf_scores.get(item['id'], 0.0) + (1.0 / (k + rank + 1))
            
        merged = []
        item_map = {item['id']: item for item in listings}
        for item_id, rrf_val in rrf_scores.items():
            if item_id in item_map:
                res = item_map[item_id].copy()
                res['score'] = round(rrf_val * 100, 3)
                merged.append(res)
                
        return sorted(merged, key=lambda x: x['score'], reverse=True)
