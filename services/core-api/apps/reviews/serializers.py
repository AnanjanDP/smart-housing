from rest_framework import serializers
from apps.reviews.models import Review
from apps.users.serializers import PublicUserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = PublicUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'reviewer', 'listing', 'target_user', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'reviewer', 'created_at')

    def validate(self, attrs):
        user = self.context['request'].user

        if self.instance is not None:
            # What was reviewed is fixed once the review exists; only the rating and comment can change.
            for field in ('listing', 'target_user'):
                if field in attrs and attrs[field] != getattr(self.instance, field):
                    raise serializers.ValidationError({field: 'This cannot be changed after the review is written.'})
            return attrs

        listing = attrs.get('listing')
        target_user = attrs.get('target_user')
        if listing is None and target_user is None:
            raise serializers.ValidationError('A review must be about a listing or a user.')
        if listing is not None and target_user is not None:
            raise serializers.ValidationError('A review can be about a listing or a user, not both.')
        if target_user is not None and target_user == user:
            raise serializers.ValidationError({'target_user': 'You cannot review yourself.'})
        if listing is not None and listing.owner_id == user.id:
            raise serializers.ValidationError({'listing': 'You cannot review your own listing.'})
        if Review.objects.filter(reviewer=user, listing=listing, target_user=target_user).exists():
            raise serializers.ValidationError('You have already reviewed this.')
        return attrs
