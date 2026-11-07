from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.repositories.listing_repository import ListingRepository, ListingRepositoryError

UPDATED = datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc)


class FakeCursor:
    def __init__(self, rows, recorder):
        self.rows = rows
        self.recorder = recorder

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.recorder.append((sql, params))

    def fetchall(self):
        return self.rows


class FakeConn:
    def __init__(self, rows, recorder, fail=False):
        self.rows = rows
        self.recorder = recorder
        self.fail = fail

    def cursor(self, cursor_factory=None):
        if self.fail:
            raise RuntimeError("connection lost")
        return FakeCursor(self.rows, self.recorder)

    def rollback(self):
        pass


class FakePool:
    def __init__(self, rows=None, fail=False):
        self.recorder = []
        self.rows = rows or []
        self.fail = fail
        self.returned = []

    def getconn(self):
        return FakeConn(self.rows, self.recorder, self.fail)

    def putconn(self, conn, close=False):
        self.returned.append(close)


@pytest.fixture
def repo(monkeypatch):
    def make(rows=None, fail=False):
        pool = FakePool(rows, fail)
        monkeypatch.setattr(ListingRepository, "_pool", pool)
        monkeypatch.setattr(ListingRepository, "_init_pool", lambda self: None)
        return ListingRepository(), pool

    return make


def test_fetch_listing_versions_maps_id_to_iso_timestamp(repo):
    repository, _ = repo([{"id": "abc", "updated_at": UPDATED}])
    assert repository.fetch_listing_versions() == {"abc": UPDATED.isoformat()}


def test_fetch_listings_by_ids_converts_types_and_passes_ids(repo):
    row = {"id": "abc", "title": "T", "description": "D", "city": "Pune", "state": "MH",
           "price": Decimal("9000.50"), "bedrooms": 1, "is_available": True, "updated_at": UPDATED}
    repository, pool = repo([row])

    listings = repository.fetch_listings_by_ids(["abc"])

    assert listings[0]["price"] == 9000.5
    assert listings[0]["updated_at"] == UPDATED.isoformat()
    sql, params = pool.recorder[0]
    assert "id = ANY(%s::uuid[])" in sql
    assert params == (["abc"],)


def test_fetch_listings_by_ids_with_no_ids_skips_the_query(repo):
    repository, pool = repo()
    assert repository.fetch_listings_by_ids([]) == []
    assert pool.recorder == []


def test_database_failure_raises_instead_of_returning_an_empty_list(repo):
    repository, pool = repo(fail=True)
    with pytest.raises(ListingRepositoryError):
        repository.fetch_listing_versions()
    assert pool.returned == [True]
    assert ListingRepository._pool is None


def test_missing_pool_raises(monkeypatch):
    monkeypatch.setattr(ListingRepository, "_pool", None)
    monkeypatch.setattr(ListingRepository, "_init_pool", lambda self: None)
    with pytest.raises(ListingRepositoryError):
        ListingRepository().fetch_listing_versions()
