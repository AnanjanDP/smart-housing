from django.contrib import admin
from apps.listings.models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'city', 'price', 'bedrooms', 'is_available', 'created_at')
    list_filter = ('is_available', 'city', 'bedrooms')
    search_fields = ('title', 'city', 'address')
