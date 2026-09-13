from rest_framework import serializers
from apps.reviews.models import Review
from apps.users.serializers import UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'reviewer', 'listing', 'target_user', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'reviewer', 'created_at')
