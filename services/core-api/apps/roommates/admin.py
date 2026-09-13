from django.contrib import admin
from apps.roommates.models import RoommateProfile

@admin.register(RoommateProfile)
class RoommateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'budget_min', 'budget_max', 'cleanliness_level', 'sleep_schedule', 'created_at')
    search_fields = ('user__email', 'preferred_location')
