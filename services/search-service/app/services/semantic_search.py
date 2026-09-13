from typing import List, Dict, Any

class SemanticSearchEngine:
    @staticmethod
    def vector_search(query: str, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simulates vector embeddings cosine similarity search
        results = []
        for listing in listings:
            # mock vector similarity calculation score
            similarity = 0.88 if 'studio' in query.lower() or 'flat' in query.lower() else 0.75
            item = listing.copy()
            item['score'] = similarity
            results.append(item)
        return sorted(results, key=lambda x: x['score'], reverse=True)
