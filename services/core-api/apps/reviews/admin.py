from django.contrib import admin
from apps.reviews.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'listing', 'target_user', 'rating', 'created_at')
    list_filter = ('rating',)
