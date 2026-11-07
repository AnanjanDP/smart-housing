from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from apps.roommates.models import RoommateProfile
from apps.roommates.serializers import RoommateProfileSerializer
from apps.roommates.matching import RoommateMatcher
from apps.roommates.permissions import IsProfileOwnerOrReadOnly

class RoommateProfileViewSet(viewsets.ModelViewSet):
    queryset = RoommateProfile.objects.all()
    serializer_class = RoommateProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly]

    def perform_create(self, serializer):
        if RoommateProfile.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError('You already have a roommate profile; update it instead.')
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def compatibility(self, request, pk=None):
        target_profile = self.get_object()
        user_profile = getattr(request.user, 'roommate_profile', None)
        if not user_profile:
            return Response({'error': 'You must create a roommate profile first.'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"roommate_compat_{user_profile.id}_{target_profile.id}"
        cached_score = cache.get(cache_key)
        if cached_score is not None:
            return Response({
                'target_user': target_profile.user.email,
                'compatibility_score': cached_score,
                'cached': True
            })

        score = RoommateMatcher.calculate_compatibility(user_profile, target_profile)
        cache.set(cache_key, score, timeout=600)  # Cache compatibility for 10 minutes

        return Response({
            'target_user': target_profile.user.email,
            'compatibility_score': score
        })

