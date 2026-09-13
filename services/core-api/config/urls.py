from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'core-api'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/listings/', include('apps.listings.urls')),
    path('api/v1/roommates/', include('apps.roommates.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/applications/', include('apps.applications.urls')),
    path('api/v1/interactions/', include('apps.interactions.urls')),
    path("", include("django_prometheus.urls")),
    
]
