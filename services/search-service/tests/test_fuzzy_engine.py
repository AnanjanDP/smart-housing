import pytest

from app.services.fuzzy_search import FuzzySearchEngine
from app.services.index_manager import IndexManager, SearchFilters, set_index_manager
from fastapi.testclient import TestClient
from helpers import CountingEmbedder, FakeRepo, sample_catalogue


class TrigramRepo(FakeRepo):
    """FakeRepo that also answers trigram queries from a canned table."""

    def __init__(self, listings, matches=None, error=None):
        super().__init__(listings)
        self.matches = matches or []
        self.error = error
        self.calls = []

    def fuzzy_search(self, terms, min_similarity=0.45, limit=100):
        self.calls.append((list(terms), limit))
        if self.error:
            raise self.error
        return self.matches


def build(matches=None, error=None):
    repo = TrigramRepo(sample_catalogue(), matches, error)
    manager = IndexManager(repo, CountingEmbedder(), index_dir=None, refresh_interval=0)
    manager.refresh()
    return repo, manager


def test_matches_become_ranked_listings_from_the_snapshot():
    _, manager = build([{"id": "c", "score": 0.9}, {"id": "a", "score": 0.5}])
    results = FuzzySearchEngine.search(manager, manager.snapshot, "studo near metro", 10)
    assert [r["id"] for r in results] == ["c", "a"]
    assert results[0]["title"] == "Budget single room"
    assert results[0]["score"] == 0.9


def test_stop_words_are_not_sent_to_the_database():
    repo, manager = build([])
    FuzzySearchEngine.search(manager, manager.snapshot, "a studio in the city", 10)
    assert repo.calls[0][0] == ["studio", "city"]


def test_matches_outside_the_snapshot_are_dropped():
    _, manager = build([{"id": "ghost", "score": 0.9}, {"id": "a", "score": 0.4}])
    assert [r["id"] for r in FuzzySearchEngine.search(manager, manager.snapshot, "studio", 10)] == ["a"]


def test_filters_are_applied():
    _, manager = build([{"id": "a", "score": 0.9}, {"id": "c", "score": 0.8}])
    results = FuzzySearchEngine.search(manager, manager.snapshot, "room", 10, SearchFilters(city="Mumbai"))
    assert [r["id"] for r in results] == ["c"]


def test_the_limit_is_applied():
    _, manager = build([{"id": "a", "score": 0.9}, {"id": "b", "score": 0.8}, {"id": "c", "score": 0.7}])
    assert len(FuzzySearchEngine.search(manager, manager.snapshot, "room", 2)) == 2


def test_a_database_failure_returns_nothing_instead_of_failing():
    _, manager = build(error=RuntimeError("database is down"))
    assert FuzzySearchEngine.search(manager, manager.snapshot, "studio", 10) == []


def test_a_repository_without_trigram_support_returns_nothing(manager):
    assert FuzzySearchEngine.search(manager, manager.snapshot, "studio", 10) == []


def test_a_query_of_only_stop_words_returns_nothing():
    repo, manager = build([{"id": "a", "score": 1}])
    assert FuzzySearchEngine.search(manager, manager.snapshot, "in the a", 10) == []
    assert repo.calls == []


# ------------------------------------------------------------------ through the API
@pytest.fixture
def api():
    repo, manager = build([{"id": "d", "score": 0.8}])
    set_index_manager(manager)
    return TestClient(__import__("app.main", fromlist=["app"]).app), repo


def test_the_fuzzy_mode_returns_trigram_results(api):
    client, _ = api
    body = client.post("/api/v1/search/query", json={"query": "penthuse", "mode": "fuzzy"}).json()
    assert body["mode"] == "fuzzy_trigram"
    assert [r["id"] for r in body["results"]] == ["d"]


def test_hybrid_search_includes_typo_matches(api):
    client, _ = api
    # "penthuse" matches nothing by keyword; the trigram leg is what brings the penthouse in.
    body = client.post("/api/v1/search/query", json={"query": "penthuse", "mode": "hybrid", "limit": 10}).json()
    assert "d" in [r["id"] for r in body["results"]]


def test_hybrid_search_still_works_when_the_trigram_leg_fails():
    _, manager = build(error=RuntimeError("database is down"))
    set_index_manager(manager)
    from app.main import app

    response = TestClient(app).post("/api/v1/search/query", json={"query": "studio metro", "mode": "hybrid"})
    assert response.status_code == 200
    assert response.json()["results"]
