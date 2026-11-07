import re
from typing import List, Dict, Any

# Function words carry no search signal; counting them made almost every listing "match".
STOP_WORDS = frozenset(
    "a an the i me my we our you your he she it its they them their this that these those "
    "is are am was were be been being to of in on at by for with and or but if as from into "
    "have has had do does did can could would should will shall may might not no so than too very".split()
)
MIN_PREFIX_LENGTH = 3


def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


class KeywordSearchEngine:
    @staticmethod
    def query_terms(query: str) -> List[str]:
        return [t for t in tokenize(query) if t not in STOP_WORDS]

    @staticmethod
    def _matches(term: str, words: set) -> bool:
        """A term matches a whole word, or (for terms of 3+ letters) the start of a word: "bed" finds "bedroom"."""
        if term in words:
            return True
        return len(term) >= MIN_PREFIX_LENGTH and any(word.startswith(term) for word in words)

    @staticmethod
    def search(query: str, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        terms = KeywordSearchEngine.query_terms(query)
        if not terms:
            return []
        results = []
        for listing in listings:
            text = " ".join(
                str(listing.get(field) or "") for field in ("title", "description", "city")
            )
            words = set(tokenize(text))
            matches = sum(1 for term in terms if KeywordSearchEngine._matches(term, words))
            if matches > 0:
                item = listing.copy()
                item['score'] = round(matches / len(terms), 2)
                results.append(item)
        return sorted(results, key=lambda x: (-x['score'], x['id']))
