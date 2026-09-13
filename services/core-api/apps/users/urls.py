from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.views import RegisterView, UserMeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', UserMeView.as_view(), name='user-me'),
]
