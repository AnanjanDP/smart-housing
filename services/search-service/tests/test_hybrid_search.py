import pytest

from app.services.hybrid_search import RRF_K, HybridSearchEngine
from app.services.index_manager import SearchFilters
from app.services.keyword_search import KeywordSearchEngine
from app.services.semantic_search import SemanticSearchEngine


def doc(listing_id):
    return {"id": listing_id, "title": listing_id, "description": "", "city": "x"}


def test_rrf_scores_follow_the_formula():
    keyword = [doc("a"), doc("b")]
    semantic = [doc("b"), doc("c")]

    fused = {r["id"]: r["score"] for r in HybridSearchEngine.fuse([keyword, semantic])}

    assert fused["a"] == pytest.approx(100 / (RRF_K + 1), abs=1e-3)
    assert fused["b"] == pytest.approx(100 * (1 / (RRF_K + 2) + 1 / (RRF_K + 1)), abs=1e-3)
    assert fused["c"] == pytest.approx(100 / (RRF_K + 2), abs=1e-3)


def test_listing_found_by_both_retrievers_outranks_listing_found_by_one():
    keyword = [doc("only_keyword"), doc("both")]
    semantic = [doc("only_semantic"), doc("both")]
    assert HybridSearchEngine.fuse([keyword, semantic])[0]["id"] == "both"


def test_fusion_is_deterministic_on_ties():
    first = HybridSearchEngine.fuse([[doc("b")], [doc("a")]])
    assert [r["id"] for r in first] == ["a", "b"]


def test_fusion_of_nothing_is_empty():
    assert HybridSearchEngine.fuse([[], []]) == []


def test_keyword_engine_scores_the_share_of_matching_terms(manager):
    results = KeywordSearchEngine.search("studio metro garden", list(manager.snapshot.docs.values()))
    by_id = {r["id"]: r["score"] for r in results}
    assert by_id["a"] == pytest.approx(0.67, abs=0.01)
    assert by_id["b"] == pytest.approx(0.33, abs=0.01)
    assert "c" not in by_id


def test_keyword_engine_tolerates_missing_fields():
    assert KeywordSearchEngine.search("x", [{"id": "1", "title": "x"}])[0]["id"] == "1"


def test_semantic_engine_returns_listing_documents_with_a_score(manager):
    results = SemanticSearchEngine.search(manager, manager.snapshot, "studio near metro", 2)
    assert results[0]["id"] == "a"
    assert {"title", "city", "price", "bedrooms", "score"} <= set(results[0])
    assert results[0]["score"] >= results[1]["score"]


def test_semantic_engine_respects_filters(manager):
    results = SemanticSearchEngine.search(
        manager, manager.snapshot, "studio near metro", 5, SearchFilters(city="Mumbai")
    )
    assert {r["id"] for r in results} == {"c", "d"}


def test_hybrid_search_puts_the_best_overall_match_first(manager):
    results = HybridSearchEngine.hybrid_search(manager, manager.snapshot, "studio near metro", None, 5)
    assert results[0]["id"] == "a"


def test_hybrid_search_applies_filters_to_both_retrievers(manager):
    results = HybridSearchEngine.hybrid_search(
        manager, manager.snapshot, "studio near metro", SearchFilters(max_price=6000), 5
    )
    assert {r["id"] for r in results} == {"c"}


# ---------------------------------------------------------------- keyword matching rules
def test_common_words_are_not_search_terms():
    assert KeywordSearchEngine.query_terms("I have a puppy in the flat") == ["puppy", "flat"]


def test_a_query_of_only_common_words_matches_nothing():
    listings = [{"id": "1", "title": "A studio in the city", "description": "I like it", "city": "Pune"}]
    assert KeywordSearchEngine.search("a the of", listings) == []


def test_matching_is_by_whole_word_not_by_substring():
    listings = [{"id": "1", "title": "Private room", "description": "Quiet", "city": "Pune"}]
    assert KeywordSearchEngine.search("rivat", listings) == []
    assert KeywordSearchEngine.search("ate", listings) == []
    assert KeywordSearchEngine.search("private", listings)[0]["id"] == "1"


def test_longer_terms_match_the_start_of_a_word():
    listings = [{"id": "1", "title": "Two bedroom flat", "description": "Near the metro", "city": "Pune"}]
    assert KeywordSearchEngine.search("bed", listings)[0]["id"] == "1"
    assert KeywordSearchEngine.search("metr", listings)[0]["id"] == "1"
    assert KeywordSearchEngine.search("be", listings) == []


def test_common_words_do_not_distort_the_ranking():
    listings = [
        {"id": "garden", "title": "House with a garden", "description": "A quiet street", "city": "Pune"},
        {"id": "pets", "title": "Flat", "description": "Welcomes dogs and puppy owners", "city": "Pune"},
    ]
    assert KeywordSearchEngine.search("I have a puppy", listings)[0]["id"] == "pets"
