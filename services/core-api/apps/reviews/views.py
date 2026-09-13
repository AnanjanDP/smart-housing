from rest_framework import viewsets, permissions
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['listing', 'target_user', 'rating']

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
