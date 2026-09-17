from apps.listings.models import Listing
from common.kafka import publish_event

class ListingService:
    @staticmethod
    def create_listing(owner, validated_data):
        listing = Listing.objects.create(owner=owner, **validated_data)
        event_payload = {
            "event_type": "LISTING_CREATED",
            "listing_id": str(listing.id),
            "title": listing.title,
            "city": listing.city,
            "price": float(listing.price),
            "owner_id": str(owner.id)
        }
        publish_event("listing_events", event_payload)
        return listing

    @staticmethod
    def get_available_listings():
        return Listing.objects.filter(is_available=True)
