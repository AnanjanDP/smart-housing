from django.contrib import admin
from apps.applications.models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'listing', 'status', 'move_in_date', 'created_at')
    list_filter = ('status',)
