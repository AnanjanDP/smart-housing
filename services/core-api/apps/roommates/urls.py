from rest_framework.routers import DefaultRouter
from apps.roommates.views import RoommateProfileViewSet

router = DefaultRouter()
router.register(r'profiles', RoommateProfileViewSet, basename='roommate-profile')

urlpatterns = router.urls
