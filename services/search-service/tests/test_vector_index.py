import numpy as np
import pytest

from app.services.embedding import HashingEmbedder, listing_text
from app.services.vector_index import (
    build_snapshot,
    empty_snapshot,
    search,
    snapshot_vectors,
)

LISTINGS = [
    {"id": "a", "title": "Sunny studio near metro", "description": "Bright studio apartment close to the metro station",
     "city": "Pune", "state": "MH", "price": 9000.0, "bedrooms": 1},
    {"id": "b", "title": "Spacious family home", "description": "Three bedroom house with garden and parking",
     "city": "Pune", "state": "MH", "price": 25000.0, "bedrooms": 3},
    {"id": "c", "title": "Budget single room", "description": "Cheap single room for students near the college",
     "city": "Mumbai", "state": "MH", "price": 5000.0, "bedrooms": 1},
    {"id": "d", "title": "Luxury penthouse", "description": "Penthouse with sea view and a rooftop pool",
     "city": "Mumbai", "state": "MH", "price": 90000.0, "bedrooms": 4},
    {"id": "e", "title": "Cozy flat", "description": "Cozy flat near the metro and the market",
     "city": "Delhi", "state": "DL", "price": 12000.0, "bedrooms": 2},
]

EMBEDDER = HashingEmbedder()


def make_snapshot(listings):
    vectors = EMBEDDER.encode([listing_text(l) for l in listings])
    ids = [l["id"] for l in listings]
    return build_snapshot(
        ids,
        {l["id"]: l for l in listings},
        {l["id"]: "v1" for l in listings},
        vectors,
        EMBEDDER.name,
        EMBEDDER.dim,
    ), vectors


def query_vector(text):
    return EMBEDDER.encode([text])[0]


def test_most_relevant_listing_ranks_first():
    snapshot, _ = make_snapshot(LISTINGS)
    results = search(snapshot, query_vector("sunny studio near metro"), k=3)
    assert results[0][0] == "a"
    assert len(results) == 3


def test_scores_are_sorted_descending():
    snapshot, _ = make_snapshot(LISTINGS)
    scores = [score for _, score in search(snapshot, query_vector("cozy flat near market"), k=5)]
    assert scores == sorted(scores, reverse=True)


def test_search_is_exact_and_matches_brute_force():
    snapshot, vectors = make_snapshot(LISTINGS)
    query = query_vector("penthouse with a pool")
    expected_order = [LISTINGS[i]["id"] for i in np.argsort(-(vectors @ query))]
    assert [i for i, _ in search(snapshot, query, k=5)] == expected_order


def test_filter_restricts_results_to_allowed_ids():
    snapshot, _ = make_snapshot(LISTINGS)
    results = search(snapshot, query_vector("studio near metro"), k=5, allowed_ids={"c", "d"})
    assert {i for i, _ in results} == {"c", "d"}


def test_filtered_search_matches_brute_force_on_the_allowed_subset():
    snapshot, vectors = make_snapshot(LISTINGS)
    query = query_vector("studio near the metro")
    allowed = {"b", "c", "e"}
    positions = [i for i, l in enumerate(LISTINGS) if l["id"] in allowed]
    expected = [LISTINGS[positions[i]]["id"] for i in np.argsort(-(vectors[positions] @ query))]
    assert [i for i, _ in search(snapshot, query, k=3, allowed_ids=allowed)] == expected


def test_prefilter_still_returns_k_results_when_top_hits_are_excluded():
    # 40 listings that mention "metro" and 5 that do not. Ask for 5 results restricted to the 5 that do
    # not. A search-then-filter approach would find none of them in the top 5.
    metro = [
        {"id": f"m{i}", "title": "Studio near metro", "description": "Close to the metro station",
         "city": "Pune", "state": "MH", "price": 9000.0, "bedrooms": 1}
        for i in range(40)
    ]
    others = [
        {"id": f"o{i}", "title": "Farmhouse", "description": "Quiet farmhouse with orchard",
         "city": "Nashik", "state": "MH", "price": 7000.0, "bedrooms": 2}
        for i in range(5)
    ]
    snapshot, _ = make_snapshot(metro + others)
    allowed = {l["id"] for l in others}
    results = search(snapshot, query_vector("studio near metro station"), k=5, allowed_ids=allowed)
    assert {i for i, _ in results} == allowed


def test_k_larger_than_index_returns_every_listing():
    snapshot, _ = make_snapshot(LISTINGS)
    assert len(search(snapshot, query_vector("anything"), k=100)) == len(LISTINGS)


def test_non_positive_k_returns_nothing():
    snapshot, _ = make_snapshot(LISTINGS)
    assert search(snapshot, query_vector("studio"), k=0) == []


def test_empty_snapshot_returns_nothing():
    snapshot = empty_snapshot(EMBEDDER.name, EMBEDDER.dim)
    assert snapshot.size == 0
    assert search(snapshot, query_vector("studio"), k=5) == []


def test_unknown_allowed_ids_return_nothing():
    snapshot, _ = make_snapshot(LISTINGS)
    assert search(snapshot, query_vector("studio"), k=5, allowed_ids={"zzz"}) == []
    assert search(snapshot, query_vector("studio"), k=5, allowed_ids=set()) == []


def test_query_dimension_mismatch_is_rejected():
    snapshot, _ = make_snapshot(LISTINGS)
    with pytest.raises(ValueError):
        search(snapshot, np.zeros(EMBEDDER.dim + 1, dtype=np.float32), k=3)


def test_duplicate_ids_are_rejected():
    vectors = EMBEDDER.encode(["a", "b"])
    with pytest.raises(ValueError):
        build_snapshot(["x", "x"], {"x": {}}, {"x": "v"}, vectors, EMBEDDER.name, EMBEDDER.dim)


def test_vector_shape_mismatch_is_rejected():
    with pytest.raises(ValueError):
        build_snapshot(["x"], {"x": {}}, {"x": "v"}, np.zeros((2, EMBEDDER.dim)), EMBEDDER.name, EMBEDDER.dim)


def test_snapshot_vectors_round_trip():
    snapshot, vectors = make_snapshot(LISTINGS)
    assert np.allclose(snapshot_vectors(snapshot), vectors)
