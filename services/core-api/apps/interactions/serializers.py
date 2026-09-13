from rest_framework import serializers
from apps.interactions.models import Interaction

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ('id', 'user', 'listing', 'action', 'timestamp')
        read_only_fields = ('id', 'user', 'timestamp')
