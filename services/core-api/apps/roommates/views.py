from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.roommates.models import RoommateProfile
from apps.roommates.serializers import RoommateProfileSerializer
from apps.roommates.matching import RoommateMatcher

class RoommateProfileViewSet(viewsets.ModelViewSet):
    queryset = RoommateProfile.objects.all()
    serializer_class = RoommateProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def compatibility(self, request, pk=None):
        target_profile = self.get_object()
        user_profile = getattr(request.user, 'roommate_profile', None)
        if not user_profile:
            return Response({'error': 'You must create a roommate profile first.'}, status=status.HTTP_400_BAD_REQUEST)
        
        score = RoommateMatcher.calculate_compatibility(user_profile, target_profile)
        return Response({
            'target_user': target_profile.user.email,
            'compatibility_score': score
        })
