from rest_framework import viewsets, permissions
from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer
from apps.listings.filters import ListingFilter
from apps.listings.permissions import IsListingOwnerOrReadOnly

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'address']
    ordering_fields = ['price', 'created_at']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsListingOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
