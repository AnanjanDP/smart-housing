"""Personalised listing recommendations.

Each listing becomes a feature vector (price, bedrooms, bathrooms and the amenities it offers). A user's
taste is the weighted average of the vectors of listings they interacted with (applying counts more than
saving, saving more than clicking, clicking more than viewing). A listing's score blends

  * similarity  cosine similarity between the listing and the user's taste,
  * budget      whether the price fits the budget on the user's roommate profile,
  * location    whether the listing is in the area the user prefers.

A component the user gives no signal for (no interactions, no profile) is left out and the rest are
re-weighted, so a brand-new user still gets a sensible, explained ordering instead of a random one.
"""
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from app.services.similarity import cosine_similarity

ACTION_WEIGHTS = {"APPLY": 3.0, "SAVE": 2.0, "CLICK": 1.0, "VIEW": 0.5}
COMPONENT_WEIGHTS = {"similarity": 0.5, "budget": 0.3, "location": 0.2}

Listing = Dict[str, Any]


def _amenity_keys(listings: Sequence[Listing]) -> List[str]:
    keys = set()
    for listing in listings:
        amenities = listing.get("amenities") or {}
        if isinstance(amenities, dict):
            keys.update(k for k, v in amenities.items() if v)
    return sorted(keys)


def _scaler(values: Sequence[float]):
    low, high = min(values), max(values)
    if high == low:
        return lambda x: 0.5
    return lambda x: (x - low) / (high - low)


class FeatureSpace:
    """Turns listings into comparable vectors, scaled and centred over the listings being compared."""

    def __init__(self, listings: Sequence[Listing]):
        self.amenity_keys = _amenity_keys(listings)
        self._scale_price = _scaler([float(x["price"]) for x in listings])
        self._scale_beds = _scaler([float(x.get("bedrooms") or 0) for x in listings])
        self._scale_baths = _scaler([float(x.get("bathrooms") or 0) for x in listings])
        raw = np.array([self._raw(x) for x in listings])
        # Centring makes "more expensive than usual" and "cheaper than usual" point in opposite directions,
        # which is what gives the cosine its meaning (otherwise every listing looks similar to every other).
        self._mean = raw.mean(axis=0)

    def _raw(self, listing: Listing) -> List[float]:
        amenities = listing.get("amenities") or {}
        flags = [1.0 if isinstance(amenities, dict) and amenities.get(k) else 0.0 for k in self.amenity_keys]
        return [
            self._scale_price(float(listing["price"])),
            self._scale_beds(float(listing.get("bedrooms") or 0)),
            self._scale_baths(float(listing.get("bathrooms") or 0)),
            *flags,
        ]

    def vector(self, listing: Listing) -> np.ndarray:
        return np.array(self._raw(listing)) - self._mean


def budget_fit(price: float, budget_min: Optional[float], budget_max: Optional[float]) -> Optional[float]:
    """1.0 inside the budget, falling to 0 as the price moves 50% outside it."""
    if budget_min is None or budget_max is None:
        return None
    if budget_min <= price <= budget_max:
        return 1.0
    if price < budget_min:
        gap = (budget_min - price) / budget_min if budget_min else 0.0
    else:
        gap = (price - budget_max) / budget_max if budget_max else 1.0
    return max(0.0, 1.0 - 2.0 * gap)


def location_fit(listing: Listing, preferred: Optional[str]) -> Optional[float]:
    if not preferred or not preferred.strip():
        return None
    wanted = preferred.strip().lower()
    places = f"{listing.get('city', '')} {listing.get('state', '')}".lower()
    return 1.0 if wanted in places or (listing.get("city") or "").lower() in wanted else 0.0


class ListingRecommenderModel:
    def recommend(self, candidates: List[Listing], interactions: List[Dict[str, Any]],
                  profile: Optional[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
        """candidates: listings to rank (newest first). interactions: [{"action", "listing"}] for this user."""
        applied = {i["listing"]["id"] for i in interactions if i["action"] == "APPLY"}
        candidates = [c for c in candidates if c["id"] not in applied]
        if not candidates:
            return []

        interacted = [i for i in interactions if i["action"] in ACTION_WEIGHTS]
        space = FeatureSpace(candidates + [i["listing"] for i in interacted])
        taste = self._taste(space, interacted)

        budget_min = float(profile["budget_min"]) if profile and profile.get("budget_min") is not None else None
        budget_max = float(profile["budget_max"]) if profile and profile.get("budget_max") is not None else None
        preferred = profile.get("preferred_location") if profile else None

        results = []
        for position, listing in enumerate(candidates):
            parts: Dict[str, float] = {}
            reasons: List[str] = []
            if taste is not None:
                similarity = (cosine_similarity(taste, space.vector(listing)) + 1.0) / 2.0
                parts["similarity"] = similarity
                if similarity >= 0.65:
                    reasons.append("Similar to listings you viewed or saved")
            fit = budget_fit(float(listing["price"]), budget_min, budget_max)
            if fit is not None:
                parts["budget"] = fit
                if fit == 1.0:
                    reasons.append("Within your budget")
            place = location_fit(listing, preferred)
            if place is not None:
                parts["location"] = place
                if place == 1.0:
                    reasons.append("In your preferred area")

            if parts:
                total_weight = sum(COMPONENT_WEIGHTS[name] for name in parts)
                score = sum(COMPONENT_WEIGHTS[name] * value for name, value in parts.items()) / total_weight
            else:
                # No signal at all: keep the incoming (newest first) order, with a flat score.
                score = 0.5
                reasons.append("New on StayMatch")
            results.append((score, -position, {**self._summary(listing), "recommendation_score": round(100 * score, 1),
                                               "reasons": reasons}))

        results.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in results[:limit]]

    @staticmethod
    def _taste(space: FeatureSpace, interacted: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        if not interacted:
            return None
        total = sum(ACTION_WEIGHTS[i["action"]] for i in interacted)
        weighted = sum(ACTION_WEIGHTS[i["action"]] * space.vector(i["listing"]) for i in interacted)
        return weighted / total

    @staticmethod
    def _summary(listing: Listing) -> Dict[str, Any]:
        return {
            "listing_id": str(listing["id"]),
            "title": listing["title"],
            "city": listing["city"],
            "state": listing.get("state", ""),
            "price": float(listing["price"]),
            "bedrooms": int(listing.get("bedrooms") or 0),
        }
