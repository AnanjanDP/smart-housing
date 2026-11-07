import math

import pytest

from app.models.listing_recommender import ListingRecommenderModel, budget_fit, location_fit
from app.services.similarity import cosine_similarity

from tests.test_recommendations import listing

model = ListingRecommenderModel()


# ------------------------------------------------------------------ cosine similarity
def test_identical_directions_have_similarity_one_whatever_their_length():
    assert cosine_similarity([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)


def test_perpendicular_vectors_have_similarity_zero():
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_opposite_vectors_have_similarity_minus_one():
    assert cosine_similarity([1, -2], [-1, 2]) == pytest.approx(-1.0)


def test_a_known_angle():
    assert cosine_similarity([1, 0], [1, 1]) == pytest.approx(math.sqrt(2) / 2)


def test_a_zero_vector_is_similar_to_nothing():
    assert cosine_similarity([0, 0], [1, 1]) == 0.0


def test_vectors_of_different_lengths_are_an_error():
    with pytest.raises(ValueError):
        cosine_similarity([1, 2], [1, 2, 3])


# ------------------------------------------------------------------ components
def test_budget_fit():
    assert budget_fit(1000, 800, 1200) == 1.0
    assert budget_fit(1320, 800, 1200) == pytest.approx(0.8)   # 10% over
    assert budget_fit(2400, 800, 1200) == 0.0                  # far over
    assert budget_fit(1000, None, None) is None


def test_location_fit():
    assert location_fit(listing("a", 1, city="Pune"), "pune") == 1.0
    assert location_fit(listing("a", 1, city="Pune"), "Delhi") == 0.0
    assert location_fit(listing("a", 1, city="Pune", state="MH"), "MH") == 1.0
    assert location_fit(listing("a", 1), None) is None
    assert location_fit(listing("a", 1), "  ") is None


# ------------------------------------------------------------------ ranking
def ids(results):
    return [r["listing_id"] for r in results]


def test_taste_learned_from_interactions_pulls_similar_listings_up():
    cheap = [listing(f"cheap{n}", 500 + n, beds=1) for n in range(3)]
    pricey = [listing(f"pricey{n}", 4000 + n, beds=4, baths=3) for n in range(3)]
    liked = [{"action": "SAVE", "listing": listing("old", 520, beds=1)}]
    results = model.recommend(pricey + cheap, liked, profile=None)
    assert set(ids(results)[:3]) == {"cheap0", "cheap1", "cheap2"}
    assert "Similar to listings you viewed or saved" in results[0]["reasons"]


def test_taste_for_expensive_places_flips_the_ranking():
    cheap = [listing(f"cheap{n}", 500, beds=1) for n in range(3)]
    pricey = [listing(f"pricey{n}", 4000, beds=4, baths=3) for n in range(3)]
    liked = [{"action": "APPLY", "listing": listing("old", 4100, beds=4, baths=3)}]
    # the applied listing itself is not a candidate, so only look at the others
    results = model.recommend(cheap + pricey, liked, profile=None)
    assert set(ids(results)[:3]) == {"pricey0", "pricey1", "pricey2"}


def test_stronger_actions_count_for_more():
    cheap = listing("cheap", 500, beds=1)
    pricey = listing("pricey", 4000, beds=4, baths=3)
    mid = listing("mid", 2000, beds=2)
    interactions = [
        {"action": "VIEW", "listing": cheap},
        {"action": "SAVE", "listing": pricey},
    ]
    results = model.recommend([mid, listing("c2", 600), listing("p2", 3900, beds=4, baths=3)], interactions, None)
    assert ids(results)[0] == "p2"  # one save outweighs one view


def test_amenities_take_part_in_the_similarity():
    wifi = {"wifi": True, "gym": True}
    candidates = [listing("with", 1000, amenities=wifi), listing("without", 1000), listing("also-without", 1000)]
    liked = [{"action": "SAVE", "listing": listing("old", 1000, amenities=wifi)}]
    assert ids(model.recommend(candidates, liked, None))[0] == "with"


def test_a_new_user_with_a_profile_is_ranked_by_budget_and_location():
    candidates = [listing("far", 3000, city="Delhi"), listing("fit", 1000, city="Pune"), listing("pricey", 1600, city="Pune")]
    profile = {"budget_min": 800, "budget_max": 1200, "preferred_location": "Pune"}
    results = model.recommend(candidates, [], profile)
    assert ids(results) == ["fit", "pricey", "far"]
    assert results[0]["reasons"] == ["Within your budget", "In your preferred area"]
    assert results[0]["recommendation_score"] == 100.0


def test_a_user_with_no_signals_gets_the_newest_listings_in_order():
    candidates = [listing("newest", 900), listing("middle", 5000), listing("oldest", 100)]
    results = model.recommend(candidates, [], None)
    assert ids(results) == ["newest", "middle", "oldest"]
    assert {r["recommendation_score"] for r in results} == {50.0}
    assert results[0]["reasons"] == ["New on StayMatch"]


def test_listings_already_applied_to_are_not_recommended_again():
    candidates = [listing("a", 1000), listing("b", 1100)]
    applied = [{"action": "APPLY", "listing": listing("a", 1000)}]
    assert ids(model.recommend(candidates, applied, None)) == ["b"]


def test_scores_stay_within_0_and_100_and_results_are_sorted():
    candidates = [listing(str(n), 500 * (n + 1), beds=n % 4 + 1) for n in range(12)]
    liked = [{"action": "CLICK", "listing": listing("x", 2000, beds=2)}]
    profile = {"budget_min": 1000, "budget_max": 3000, "preferred_location": "pune"}
    scores = [r["recommendation_score"] for r in model.recommend(candidates, liked, profile)]
    assert all(0 <= s <= 100 for s in scores)
    assert scores == sorted(scores, reverse=True)


def test_every_listing_having_the_same_values_does_not_break_the_maths():
    candidates = [listing(str(n), 1000) for n in range(3)]
    liked = [{"action": "SAVE", "listing": listing("old", 1000)}]
    assert len(model.recommend(candidates, liked, None)) == 3


def test_the_candidate_list_is_not_modified():
    candidates = [listing("a", 1000), listing("b", 2000)]
    before = [dict(c) for c in candidates]
    model.recommend(candidates, [], None)
    assert candidates == before
