from app.repositories.listing_repository import ListingRepositoryError
from app.services.embedding import HashingEmbedder


class CountingEmbedder(HashingEmbedder):
    """Hashing embedder that records how many texts it has encoded."""

    def __init__(self, dim=128):
        super().__init__(dim)
        self.encoded_texts = 0

    def encode(self, texts):
        self.encoded_texts += len(texts)
        return super().encode(texts)


class FakeRepo:
    """In-memory stand-in for ListingRepository."""

    def __init__(self, listings):
        self.listings = {l["id"]: dict(l) for l in listings}
        self.fail = False
        self.vanish = set()

    def set(self, listing):
        self.listings[listing["id"]] = dict(listing)

    def fetch_listing_versions(self):
        if self.fail:
            raise ListingRepositoryError("database is down")
        return {i: l["updated_at"] for i, l in self.listings.items()}

    def fetch_listings_by_ids(self, ids):
        if self.fail:
            raise ListingRepositoryError("database is down")
        return [dict(self.listings[i]) for i in ids if i in self.listings and i not in self.vanish]


def listing(listing_id, title, description, city="Pune", price=10000.0, bedrooms=1, updated="2025-01-01T00:00:00"):
    return {"id": listing_id, "title": title, "description": description, "city": city, "state": "MH",
            "price": price, "bedrooms": bedrooms, "is_available": True, "updated_at": updated}


def sample_catalogue():
    return [
        listing("a", "Sunny studio near metro", "Bright studio apartment close to the metro station"),
        listing("b", "Spacious family home", "Three bedroom house with garden and parking", price=25000.0, bedrooms=3),
        listing("c", "Budget single room", "Cheap single room for students", city="Mumbai", price=5000.0),
        listing("d", "Luxury penthouse", "Penthouse with sea view and rooftop pool", city="Mumbai", price=90000.0, bedrooms=4),
    ]
