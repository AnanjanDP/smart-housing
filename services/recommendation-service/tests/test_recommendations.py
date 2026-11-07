import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_repository
from app.main import app
from app.repositories.recommendation_repository import RepositoryError

KEY = "k" * 40
ME = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"


def listing(id_, price, city="Pune", beds=1, baths=1, amenities=None, state="MH"):
    return {"id": id_, "title": f"Listing {id_}", "city": city, "state": state, "price": price,
            "bedrooms": beds, "bathrooms": baths, "amenities": amenities or {}}


class FakeRepository:
    def __init__(self, candidates=(), interactions=(), profile=None, error=None):
        self.candidates, self.interactions, self.profile, self.error = list(candidates), list(interactions), profile, error
        self.asked_for = []

    def _check(self, user_id):
        self.asked_for.append(user_id)
        if self.error:
            raise self.error

    def fetch_candidates(self, user_id):
        self._check(user_id)
        return self.candidates

    def fetch_interactions(self, user_id):
        return self.interactions

    def fetch_profile(self, user_id):
        return self.profile


def token(user_id=ME, **overrides):
    claims = {"user_id": user_id, "token_type": "access", "exp": int(time.time()) + 600}
    claims.update(overrides)
    return jwt.encode(claims, KEY, algorithm="HS256")


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setenv("JWT_SIGNING_KEY", KEY)
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def use(repository):
    app.dependency_overrides[get_repository] = lambda: repository
    return repository


def get(client, user_id=ME, bearer=None, **params):
    headers = {"Authorization": f"Bearer {bearer}"} if bearer else {}
    return client.get(f"/api/v1/recommendations/listings/{user_id}", headers=headers, params=params)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "recommendation-service"


# ------------------------------------------------------------------ access control
def test_a_token_is_required(client):
    use(FakeRepository([listing("a", 1000)]))
    assert get(client).status_code == 401


@pytest.mark.parametrize("bad", ["abc", "a.b.c"])
def test_malformed_tokens_are_refused(client, bad):
    use(FakeRepository([listing("a", 1000)]))
    assert get(client, bearer=bad).status_code == 401


def test_a_token_signed_with_another_key_is_refused(client):
    use(FakeRepository([listing("a", 1000)]))
    forged = jwt.encode({"user_id": ME, "token_type": "access", "exp": int(time.time()) + 60}, "x" * 40, algorithm="HS256")
    assert get(client, bearer=forged).status_code == 401


def test_expired_and_refresh_tokens_are_refused(client):
    use(FakeRepository([listing("a", 1000)]))
    assert get(client, bearer=token(exp=int(time.time()) - 5)).status_code == 401
    assert get(client, bearer=token(token_type="refresh")).status_code == 401


def test_nothing_is_accepted_when_the_key_is_not_configured(client, monkeypatch):
    monkeypatch.setenv("JWT_SIGNING_KEY", "")
    use(FakeRepository([listing("a", 1000)]))
    assert get(client, bearer=token()).status_code == 401


def test_you_cannot_read_someone_elses_recommendations(client):
    repo = use(FakeRepository([listing("a", 1000)]))
    assert get(client, user_id=OTHER, bearer=token()).status_code == 403
    assert repo.asked_for == []


def test_a_user_id_that_is_not_a_uuid_is_not_found(client):
    assert get(client, user_id="user-123", bearer=token()).status_code == 404


# ------------------------------------------------------------------ behaviour
def test_recommendations_are_returned_with_scores_and_reasons(client):
    use(FakeRepository(
        [listing("a", 1000), listing("b", 5000)],
        profile={"budget_min": 800, "budget_max": 1200, "preferred_location": "Pune"}))
    response = get(client, bearer=token())
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == ME
    assert [r["listing_id"] for r in body["recommendations"]] == ["a", "b"]
    best = body["recommendations"][0]
    assert best["recommendation_score"] > body["recommendations"][1]["recommendation_score"]
    assert "Within your budget" in best["reasons"]


def test_no_listings_gives_an_empty_list_not_an_error(client):
    use(FakeRepository([]))
    response = get(client, bearer=token())
    assert response.status_code == 200
    assert response.json()["recommendations"] == []


def test_the_limit_is_applied_and_validated(client):
    use(FakeRepository([listing(str(n), 1000 + n) for n in range(10)]))
    assert len(get(client, bearer=token(), limit=3).json()["recommendations"]) == 3
    assert get(client, bearer=token(), limit=0).status_code == 422
    assert get(client, bearer=token(), limit=1000).status_code == 422


def test_a_database_outage_is_reported_not_hidden(client):
    use(FakeRepository(error=RepositoryError("database unavailable: password=secret")))
    response = get(client, bearer=token())
    assert response.status_code == 503
    assert "secret" not in response.text
