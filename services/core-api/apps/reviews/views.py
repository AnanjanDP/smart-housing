from rest_framework import viewsets, permissions
from apps.reviews.models import Review
from apps.reviews.permissions import IsReviewAuthorOrReadOnly
from apps.reviews.serializers import ReviewSerializer
from apps.reviews.services import ReviewService

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewAuthorOrReadOnly]
    filterset_fields = ['listing', 'target_user', 'rating']

    def perform_create(self, serializer):
        ReviewService.create_review(serializer, self.request.user)
