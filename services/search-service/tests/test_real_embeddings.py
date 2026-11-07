"""Checks the production embedding model end to end.

These tests download all-MiniLM-L6-v2 (about 90 MB), so they only run when asked:

    RUN_MODEL_TESTS=1 pytest tests/test_real_embeddings.py
"""
import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MODEL_TESTS") != "1",
    reason="set RUN_MODEL_TESTS=1 to download and run the real embedding model",
)

pytest.importorskip("sentence_transformers")

from app.services.embedding import SentenceTransformerEmbedder  # noqa: E402
from app.services.index_manager import IndexManager, SearchFilters  # noqa: E402
from helpers import FakeRepo, listing  # noqa: E402

CATALOGUE = [
    listing("metro", "Sunny studio near metro", "Bright studio apartment a two minute walk from the metro station",
            city="Pune", price=14000.0),
    listing("student", "Budget single room", "Affordable shared room for students close to the university campus",
            city="Pune", price=4500.0),
    listing("garden", "Family house with garden", "Spacious three bedroom house with a lawn, trees and a quiet street",
            city="Pune", price=30000.0, bedrooms=3),
    listing("pool", "Luxury penthouse", "Top floor penthouse with a rooftop swimming pool and sea views",
            city="Mumbai", price=150000.0, bedrooms=4),
    listing("tech", "Apartment in the tech park", "Modern flat beside the office towers and business district",
            city="Bengaluru", price=32000.0, bedrooms=2),
    listing("pets", "Pet friendly flat", "Ground floor flat that welcomes dogs and cats, with a park next door",
            city="Delhi", price=22000.0, bedrooms=2),
]


@pytest.fixture(scope="module")
def manager():
    m = IndexManager(FakeRepo(CATALOGUE), SentenceTransformerEmbedder(), index_dir=None)
    m.refresh()
    return m


def best(manager, query, filters=None):
    return manager.semantic_search(query, 1, filters)[0][0]


def test_model_produces_384_dimensional_vectors(manager):
    assert manager.snapshot.dim == 384
    assert manager.snapshot.model.endswith("all-MiniLM-L6-v2")


@pytest.mark.parametrize(
    "query, expected",
    [
        ("public transport nearby", "metro"),
        ("cheap place for college students", "student"),
        ("somewhere to swim", "pool"),
        ("peaceful home with greenery", "garden"),
        ("close to where I work in IT", "tech"),
        ("I have a puppy", "pets"),
    ],
)
def test_finds_listings_by_meaning_even_without_shared_words(manager, query, expected):
    assert best(manager, query) == expected


def test_filters_still_apply_with_real_embeddings(manager):
    hits = manager.semantic_search("somewhere to swim", 5, SearchFilters(city="Pune"))
    assert {i for i, _ in hits} <= {"metro", "student", "garden"}
    assert "pool" not in {i for i, _ in hits}


def test_unit_length_vectors_give_cosine_scores_in_range(manager):
    scores = [s for _, s in manager.semantic_search("studio near the metro", 6)]
    assert all(-1.0 <= s <= 1.0001 for s in scores)
    assert scores == sorted(scores, reverse=True)
