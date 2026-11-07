from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.core.cache import cache
from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer
from apps.listings.filters import ListingFilter
from apps.listings.permissions import CanPublishListings, IsListingOwnerOrReadOnly

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'address']
    ordering_fields = ['price', 'created_at']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CanPublishListings, IsListingOwnerOrReadOnly]

    def list(self, request, *args, **kwargs):
        cache_key = f"listings_list_{request.query_params.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout=120)
        return response

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        self.clear_cache()

    def perform_update(self, serializer):
        serializer.save()
        self.clear_cache()

    def perform_destroy(self, instance):
        instance.delete()
        self.clear_cache()

    def clear_cache(self):
        try:
            cache.clear()
        except Exception:
            pass

