from rest_framework import serializers
from apps.listings.models import Listing
from apps.users.serializers import PublicUserSerializer

class ListingSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ('id', 'owner', 'title', 'description', 'address', 'city', 'state', 'zip_code', 'price', 'bedrooms', 'bathrooms', 'is_available', 'amenities', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
