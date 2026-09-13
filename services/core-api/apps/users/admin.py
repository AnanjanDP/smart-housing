from django.contrib import admin
from apps.users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
