from rest_framework import serializers
from apps.roommates.models import RoommateProfile
from apps.users.serializers import UserSerializer

class RoommateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoommateProfile
        fields = ('id', 'user', 'budget_min', 'budget_max', 'move_in_date', 'cleanliness_level', 'sleep_schedule', 'smoking_allowed', 'pets_allowed', 'preferred_location', 'bio', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
