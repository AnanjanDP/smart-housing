from apps.listings.models import Listing

class ListingService:
    @staticmethod
    def create_listing(owner, validated_data):
        listing = Listing.objects.create(owner=owner, **validated_data)
        # Event publication placeholder to Kafka topic 'listing_events'
        return listing

    @staticmethod
    def get_available_listings():
        return Listing.objects.filter(is_available=True)
