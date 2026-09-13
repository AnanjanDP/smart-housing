from rest_framework import viewsets, permissions
from apps.interactions.models import Interaction
from apps.interactions.serializers import InteractionSerializer

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Interaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
