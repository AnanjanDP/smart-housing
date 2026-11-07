from rest_framework import serializers
from apps.applications.models import Application
from apps.users.serializers import UserSerializer
from apps.listings.serializers import ListingSerializer

ACTIVE_STATUSES = (Application.Status.PENDING, Application.Status.UNDER_REVIEW)

# Statuses a landlord may move an application to. Approved and rejected are final.
ALLOWED_TRANSITIONS = {
    Application.Status.PENDING: {Application.Status.UNDER_REVIEW, Application.Status.APPROVED, Application.Status.REJECTED},
    Application.Status.UNDER_REVIEW: {Application.Status.APPROVED, Application.Status.REJECTED},
    Application.Status.APPROVED: set(),
    Application.Status.REJECTED: set(),
}


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    listing_detail = ListingSerializer(source='listing', read_only=True)

    class Meta:
        model = Application
        fields = ('id', 'listing', 'listing_detail', 'applicant', 'status', 'move_in_date', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'applicant', 'created_at', 'updated_at')

    def validate(self, attrs):
        user = self.context['request'].user
        if self.instance is None:
            return self._validate_new(user, attrs)
        return self._validate_change(user, attrs)

    def _validate_new(self, user, attrs):
        listing = attrs['listing']
        if listing.owner_id == user.id:
            raise serializers.ValidationError({'listing': 'You cannot apply to your own listing.'})
        if not listing.is_available:
            raise serializers.ValidationError({'listing': 'This listing is not available.'})
        if Application.objects.filter(applicant=user, listing=listing, status__in=ACTIVE_STATUSES).exists():
            raise serializers.ValidationError({'listing': 'You already have an active application for this listing.'})
        # A new application always starts as pending, whatever the client sent.
        attrs.pop('status', None)
        return attrs

    def _validate_change(self, user, attrs):
        application = self.instance
        if 'listing' in attrs and attrs['listing'] != application.listing:
            raise serializers.ValidationError({'listing': 'The listing of an application cannot be changed.'})

        is_landlord = application.listing.owner_id == user.id
        if is_landlord:
            # The landlord decides the outcome and nothing else.
            for field in set(attrs) - {'status', 'listing'}:
                raise serializers.ValidationError({field: 'Only the applicant can change this.'})
            new_status = attrs.get('status', application.status)
            if new_status != application.status and new_status not in ALLOWED_TRANSITIONS[application.status]:
                raise serializers.ValidationError(
                    {'status': f'An application that is {application.status} cannot become {new_status}.'}
                )
            return attrs

        # The applicant can edit their own details while the application is open, but never its status.
        if 'status' in attrs and attrs['status'] != application.status:
            raise serializers.ValidationError({'status': 'Only the landlord can change the status.'})
        if application.status not in ACTIVE_STATUSES:
            raise serializers.ValidationError('A decided application can no longer be edited.')
        return attrs
