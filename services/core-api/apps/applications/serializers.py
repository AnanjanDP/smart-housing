from rest_framework import serializers
from apps.applications.models import Application
from apps.users.serializers import UserSerializer
from apps.listings.serializers import ListingSerializer

class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    listing_detail = ListingSerializer(source='listing', read_only=True)

    class Meta:
        model = Application
        fields = ('id', 'listing', 'listing_detail', 'applicant', 'status', 'move_in_date', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'applicant', 'created_at', 'updated_at')
