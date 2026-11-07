import pytest

from app.core.config import settings
from app.services.index_manager import IndexManager, set_index_manager
from helpers import CountingEmbedder, FakeRepo, listing, sample_catalogue

URL = "/api/v1/search/query"


def search(client, **body):
    body.setdefault("query", "studio near metro")
    return client.post(URL, json=body)


def ids(response):
    return [r["id"] for r in response.json()["results"]]


def test_hybrid_is_the_default_mode_and_ranks_the_best_match_first(client):
    response = search(client)
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "hybrid_rrf"
    assert body["index_version"] == 1
    assert body["results"][0]["id"] == "a"
    assert body["total"] == len(body["results"])


def test_semantic_mode_uses_the_vector_index(client):
    body = search(client, mode="semantic").json()
    assert body["mode"] == "semantic_faiss"
    assert body["results"][0]["id"] == "a"
    assert 0.0 < body["results"][0]["score"] <= 1.0


def test_keyword_mode_only_returns_listings_containing_the_words(client):
    body = search(client, mode="keyword", query="penthouse").json()
    assert body["mode"] == "keyword"
    assert [r["id"] for r in body["results"]] == ["d"]


def test_filters_apply_in_every_mode(client):
    for mode in ("hybrid", "semantic", "keyword"):
        assert set(ids(search(client, mode=mode, query="room", city="mumbai"))) <= {"c", "d"}
        assert set(ids(search(client, mode=mode, query="room", max_price=10000))) <= {"a", "c"}
        assert set(ids(search(client, mode=mode, query="room", min_price=20000))) <= {"b", "d"}


def test_bedrooms_filter_is_honoured(client):
    assert ids(search(client, mode="semantic", query="home", bedrooms=3)) == ["b"]
    assert ids(search(client, mode="keyword", query="home", bedrooms=1)) == []


def test_limit_caps_the_number_of_results(client):
    assert len(ids(search(client, mode="semantic", limit=2))) == 2


def test_invalid_limit_is_rejected(client):
    assert search(client, limit=0).status_code == 422
    assert search(client, limit=1000).status_code == 422


def test_unknown_mode_is_rejected(client):
    assert search(client, mode="magic").status_code == 422


def test_blank_query_browses_the_filtered_listings(client):
    body = search(client, query="  ", city="Mumbai").json()
    assert body["mode"] == "browse"
    assert {r["id"] for r in body["results"]} == {"c", "d"}
    assert all(r["score"] == 0.0 for r in body["results"])


def test_new_listings_become_searchable_after_a_refresh(client, manager, repo):
    repo.set(listing("n", "Hillside villa", "Large villa on the hillside with a view"))
    assert "n" not in ids(search(client, query="villa on the hillside", mode="keyword"))

    manager.refresh()

    response = search(client, query="villa on the hillside", mode="semantic")
    assert response.json()["results"][0]["id"] == "n"
    assert response.json()["index_version"] == 2


def test_results_do_not_expose_internal_fields(client):
    result = search(client).json()["results"][0]
    assert set(result) == {"id", "title", "description", "city", "price", "bedrooms", "score"}


# ---------------------------------------------------------------- index endpoints
def test_index_stats_report_the_live_index(client):
    stats = client.get("/api/v1/search/index/stats").json()
    assert stats["listings"] == 4
    assert stats["version"] == 1
    assert stats["last_refresh"]["added"] == 4


def test_refresh_requires_the_admin_token(client, monkeypatch):
    url = "/api/v1/search/index/refresh"
    monkeypatch.setattr(settings, "SEARCH_ADMIN_TOKEN", "")
    assert client.post(url, headers={"X-Admin-Token": ""}).status_code == 403

    monkeypatch.setattr(settings, "SEARCH_ADMIN_TOKEN", "s3cret")
    assert client.post(url).status_code == 403
    assert client.post(url, headers={"X-Admin-Token": "wrong"}).status_code == 403
    ok = client.post(url, headers={"X-Admin-Token": "s3cret"})
    assert ok.status_code == 200
    assert ok.json()["changed"] is False


def test_forced_refresh_rebuilds_the_index(client, monkeypatch):
    monkeypatch.setattr(settings, "SEARCH_ADMIN_TOKEN", "s3cret")
    body = client.post("/api/v1/search/index/refresh?force=true", headers={"X-Admin-Token": "s3cret"}).json()
    assert body["forced"] is True
    assert body["changed"] is True


def test_refresh_reports_503_when_the_database_is_down(client, repo, monkeypatch):
    monkeypatch.setattr(settings, "SEARCH_ADMIN_TOKEN", "s3cret")
    repo.fail = True
    response = client.post("/api/v1/search/index/refresh", headers={"X-Admin-Token": "s3cret"})
    assert response.status_code == 503
    assert search(client).status_code == 200


# ---------------------------------------------------------------- readiness
def test_ready_reports_warming_up_until_an_index_exists():
    from fastapi.testclient import TestClient
    from app.main import app

    set_index_manager(IndexManager(FakeRepo(sample_catalogue()), CountingEmbedder()))
    assert TestClient(app).get("/ready").status_code == 503


def test_ready_reports_listing_count_once_built(client):
    body = client.get("/ready").json()
    assert body == {"status": "ready", "service": "search-service", "listings": 4, "index_version": 1}


def test_health_does_not_depend_on_the_index(client):
    assert client.get("/health").json() == {"status": "healthy", "service": "search-service"}


def test_startup_builds_the_index_in_the_background_and_shutdown_stops_it():
    import time
    from fastapi.testclient import TestClient
    from app.main import app

    manager = IndexManager(FakeRepo(sample_catalogue()), CountingEmbedder())
    set_index_manager(manager)

    with TestClient(app) as running:
        deadline = time.time() + 5
        while time.time() < deadline and running.get("/ready").status_code != 200:
            time.sleep(0.02)
        assert running.get("/ready").status_code == 200
        assert running.post(URL, json={"query": "studio near metro"}).json()["results"][0]["id"] == "a"

    assert manager._stop.is_set()
