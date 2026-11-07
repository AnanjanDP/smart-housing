import hashlib
import logging
import time

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.core.cache import cache
from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer
from apps.listings.filters import ListingFilter
from apps.listings.permissions import CanPublishListings, IsListingOwnerOrReadOnly
from apps.listings.services import ListingService

logger = logging.getLogger(__name__)

VERSION_KEY = 'listings_list_version'


def current_version():
    """Listing pages are cached under this version; bumping it retires them all without touching other keys."""
    version = cache.get(VERSION_KEY)
    if version is None:
        cache.add(VERSION_KEY, time.time_ns(), timeout=None)
        version = cache.get(VERSION_KEY)
    return version


def bump_version():
    try:
        cache.incr(VERSION_KEY)
    except ValueError:  # the counter is missing (expired or never created)
        cache.set(VERSION_KEY, time.time_ns(), timeout=None)


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'address']
    ordering_fields = ['price', 'created_at']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CanPublishListings, IsListingOwnerOrReadOnly]

    def list(self, request, *args, **kwargs):
        try:
            query = hashlib.sha256(request.query_params.urlencode().encode()).hexdigest()
            cache_key = f"listings_list_{current_version()}_{query}"
            cached_data = cache.get(cache_key)
        except Exception:
            logger.warning("Listing cache unavailable, serving uncached", exc_info=True)
            return super().list(request, *args, **kwargs)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                cache.set(cache_key, response.data, timeout=120)
            except Exception:
                logger.warning("Could not cache listing page", exc_info=True)
        return response

    def perform_create(self, serializer):
        serializer.instance = ListingService.create_listing(self.request.user, dict(serializer.validated_data))
        self.clear_cache()

    def perform_update(self, serializer):
        serializer.save()
        self.clear_cache()

    def perform_destroy(self, instance):
        instance.delete()
        self.clear_cache()

    def clear_cache(self):
        try:
            bump_version()
        except Exception:
            logger.warning("Could not invalidate the listing cache", exc_info=True)

