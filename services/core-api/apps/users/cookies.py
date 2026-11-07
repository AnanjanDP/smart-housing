"""The refresh token travels only in an HttpOnly cookie.

Scripts on the page cannot read such a cookie, so an XSS bug cannot steal the long-lived token (the
short-lived access token is all it could reach). The cookie is only sent to the user endpoints, only
for same-site requests (SameSite=Strict, so other sites cannot trigger a refresh) and, in production, only
over HTTPS.
"""
from django.conf import settings


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        str(refresh_token),
        max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        path=settings.REFRESH_COOKIE_PATH,
        secure=settings.REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite='Strict',
    )
    return response


def clear_refresh_cookie(response):
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=settings.REFRESH_COOKIE_PATH, samesite='Strict')
    return response


def read_refresh_cookie(request):
    return request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
