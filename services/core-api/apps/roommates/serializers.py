from rest_framework import serializers
from apps.roommates.models import RoommateProfile
from apps.users.serializers import UserSerializer

class RoommateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    cleanliness_level = serializers.IntegerField(min_value=1, max_value=5, required=False)

    class Meta:
        model = RoommateProfile
        fields = ('id', 'user', 'budget_min', 'budget_max', 'move_in_date', 'cleanliness_level', 'sleep_schedule', 'smoking_allowed', 'pets_allowed', 'preferred_location', 'bio', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate(self, attrs):
        budget_min = attrs.get('budget_min', getattr(self.instance, 'budget_min', None))
        budget_max = attrs.get('budget_max', getattr(self.instance, 'budget_max', None))
        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            raise serializers.ValidationError({'budget_min': 'The minimum budget cannot exceed the maximum budget.'})
        return attrs
