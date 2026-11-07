from django.urls import path
from apps.users.views import RegisterView, UserMeView, OAuthOIDCLoginView, CustomTokenObtainPairView, LogoutView, CookieTokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('oauth/login/', OAuthOIDCLoginView.as_view(), name='oauth-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token-refresh'),
    path('me/', UserMeView.as_view(), name='user-me'),
]
