import math
import re
from typing import List, Dict, Any

class SemanticSearchEngine:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    @staticmethod
    def vector_search(query: str, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        query_tokens = SemanticSearchEngine.tokenize(query)
        if not query_tokens:
            return listings

        query_freq = {}
        for token in query_tokens:
            query_freq[token] = query_freq.get(token, 0) + 1
        query_magnitude = math.sqrt(sum(v ** 2 for v in query_freq.values()))

        results = []
        for listing in listings:
            combined_text = f"{listing.get('title', '')} {listing.get('description', '')} {listing.get('city', '')} {listing.get('state', '')}"
            doc_tokens = SemanticSearchEngine.tokenize(combined_text)
            
            doc_freq = {}
            for token in doc_tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

            dot_product = sum(query_freq[t] * doc_freq.get(t, 0) for t in query_freq)
            doc_magnitude = math.sqrt(sum(v ** 2 for v in doc_freq.values()))

            if query_magnitude > 0 and doc_magnitude > 0:
                similarity = dot_product / (query_magnitude * doc_magnitude)
            else:
                similarity = 0.0

            # Scale base similarity with a minimum floor of 0.50 for candidate ranking
            boosted_score = round(0.50 + (similarity * 0.49), 4)

            item = listing.copy()
            item['score'] = boosted_score
            results.append(item)

        return sorted(results, key=lambda x: x['score'], reverse=True)

