import django_filters
from apps.listings.models import Listing

class ListingFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    bedrooms = django_filters.NumberFilter(field_name='bedrooms')

    class Meta:
        model = Listing
        fields = ['min_price', 'max_price', 'city', 'bedrooms', 'is_available']
