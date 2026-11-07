from typing import List, Dict, Any

class KeywordSearchEngine:
    @staticmethod
    def search(query: str, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tokens = query.lower().split()
        results = []
        for listing in listings:
            text = " ".join(
                str(listing.get(field) or "") for field in ("title", "description", "city")
            ).lower()
            matches = sum(1 for token in tokens if token in text)
            if matches > 0:
                score = round(matches / len(tokens), 2)
                item = listing.copy()
                item['score'] = score
                results.append(item)
        return sorted(results, key=lambda x: (-x['score'], x['id']))
