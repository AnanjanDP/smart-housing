"""Runs the trigram query against a real PostgreSQL. Skipped unless TEST_POSTGRES_PORT is set.

It creates a minimal `listings_listing` table, so it refuses to run against any database whose name
does not start with "test_". Example:

    docker run -d -e POSTGRES_PASSWORD=pw -e POSTGRES_USER=u -e POSTGRES_DB=test_trgm -p 127.0.0.1:55432:5432 postgres:15-alpine
    TEST_POSTGRES_PORT=55432 TEST_POSTGRES_DB=test_trgm TEST_POSTGRES_USER=u TEST_POSTGRES_PASSWORD=pw pytest tests/test_fuzzy_postgres.py
"""
import os
import uuid

import pytest

from app.repositories.listing_repository import ListingRepository

PORT = os.getenv("TEST_POSTGRES_PORT")
DB = os.getenv("TEST_POSTGRES_DB", "")

pytestmark = pytest.mark.skipif(
    not PORT or not DB.startswith("test_"), reason="needs TEST_POSTGRES_PORT and a TEST_POSTGRES_DB named test_*")

ROWS = {
    "bangalore": ("Cozy studio in Indiranagar", "Bangalore", "Karnataka", "12 MG Road", True),
    "pune": ("Sunny flat near the metro", "Pune", "Maharashtra", "4 FC Road", True),
    "mumbai": ("Sea view penthouse", "Mumbai", "Maharashtra", "9 Marine Drive", True),
    "taken": ("Studio in Bangalore (taken)", "Bangalore", "Karnataka", "1 Church Street", False),
}


@pytest.fixture(scope="module")
def repo():
    import psycopg2

    params = dict(dbname=DB, user=os.getenv("TEST_POSTGRES_USER", "postgres"),
                  password=os.getenv("TEST_POSTGRES_PASSWORD", ""), host=os.getenv("TEST_POSTGRES_HOST", "127.0.0.1"),
                  port=PORT)
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    ids = {}
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        cur.execute("DROP TABLE IF EXISTS listings_listing")
        cur.execute("CREATE TABLE listings_listing (id uuid PRIMARY KEY, title text, city text, state text, "
                    "address text, is_available boolean)")
        for name, (title, city, state, address, available) in ROWS.items():
            ids[name] = str(uuid.uuid4())
            cur.execute("INSERT INTO listings_listing VALUES (%s, %s, %s, %s, %s, %s)",
                        (ids[name], title, city, state, address, available))
    conn.close()

    os.environ.update(POSTGRES_DB=DB, POSTGRES_USER=params["user"], POSTGRES_PASSWORD=params["password"],
                      POSTGRES_HOST=params["host"], POSTGRES_PORT=PORT)
    ListingRepository._pool = None
    repository = ListingRepository()
    repository.ids = ids
    yield repository
    ListingRepository._pool = None


def found(repo, *terms, **kw):
    return [r["id"] for r in repo.fuzzy_search(list(terms), **kw)]


def test_a_misspelt_city_still_finds_the_listing(repo):
    assert found(repo, "banglore")[:1] == [repo.ids["bangalore"]]


def test_a_misspelt_word_in_the_title_is_found(repo):
    assert repo.ids["bangalore"] in found(repo, "studo")


def test_an_address_can_be_matched(repo):
    assert found(repo, "marine")[:1] == [repo.ids["mumbai"]]


def test_unavailable_listings_are_never_returned(repo):
    assert repo.ids["taken"] not in found(repo, "bangalore")


def test_unrelated_terms_find_nothing(repo):
    assert found(repo, "xylophone") == []


def test_more_matching_terms_rank_higher(repo):
    ranked = found(repo, "studio", "banglore")
    assert ranked[0] == repo.ids["bangalore"]


def test_scores_are_between_zero_and_one_and_sorted(repo):
    scores = [r["score"] for r in repo.fuzzy_search(["pune", "metro", "flat"])]
    assert scores and all(0 < s <= 1.0 for s in scores) and scores == sorted(scores, reverse=True)


def test_the_limit_is_respected(repo):
    assert len(repo.fuzzy_search(["maharashtra"], limit=1)) == 1


def test_quotes_and_percent_signs_in_terms_are_harmless(repo):
    assert found(repo, "o'brien", "100%", "'; DROP TABLE listings_listing; --") is not None
    assert len(found(repo, "pune")) == 1  # the table is still there
