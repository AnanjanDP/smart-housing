import unittest
from app.services.semantic_search import SemanticSearchEngine
from app.repositories.listing_repository import ListingRepository

class TestSemanticSearch(unittest.TestCase):
    def test_semantic_search_engine(self):
        repo = ListingRepository()
        listings = repo.fetch_all_active_listings()
        results = SemanticSearchEngine.vector_search("sunny studio", listings)
        self.assertGreater(len(results), 0)
        self.assertIn("score", results[0])

if __name__ == '__main__':
    unittest.main()
