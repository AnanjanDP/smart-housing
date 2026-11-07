import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.listings.models import Listing
from apps.users.models import User

CORE_API = Path(__file__).resolve().parent.parent
GOOD_ENV = {
    "SECRET_KEY": "k" * 50,
    "ALLOWED_HOSTS": "staymatch.example",
    "POSTGRES_PASSWORD": "a-long-database-password",
}
READ_SETTINGS = (
    "import json, django; from django.conf import settings as s; "
    "print(json.dumps({'debug': s.DEBUG, 'hosts': s.ALLOWED_HOSTS, 'session_secure': s.SESSION_COOKIE_SECURE, "
    "'csrf_secure': s.CSRF_COOKIE_SECURE, 'hsts': s.SECURE_HSTS_SECONDS, 'proxies': s.REST_FRAMEWORK['NUM_PROXIES'], "
    "'cors_all': s.CORS_ALLOW_ALL_ORIGINS, 'refresh_secure': s.REFRESH_COOKIE_SECURE, 'cors': s.CORS_ALLOWED_ORIGINS, 'proxy_header': s.SECURE_PROXY_SSL_HEADER}))"
)


def load_production_settings(**env):
    """Import the production settings in a clean process and return (exit code, output, error)."""
    clean = {k: v for k, v in os.environ.items()
             if k not in ("SECRET_KEY", "ALLOWED_HOSTS", "POSTGRES_PASSWORD", "NUM_PROXIES", "CORS_ALLOWED_ORIGINS",
                          "DJANGO_SETTINGS_MODULE")}
    clean.update(env)
    clean["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    result = subprocess.run([sys.executable, "-c", READ_SETTINGS], cwd=CORE_API, env=clean,
                            capture_output=True, text=True, timeout=120)
    return result.returncode, result.stdout, result.stderr


class ProductionSettingsTests(APITestCase):
    def test_a_missing_secret_key_stops_the_app_from_starting(self):
        code, _, err = load_production_settings(**{k: v for k, v in GOOD_ENV.items() if k != "SECRET_KEY"})
        self.assertNotEqual(code, 0)
        self.assertIn("SECRET_KEY", err)

    def test_the_old_default_secret_key_is_refused(self):
        code, _, err = load_production_settings(**{**GOOD_ENV, "SECRET_KEY": "django-insecure-" + "x" * 50})
        self.assertNotEqual(code, 0)
        self.assertIn("SECRET_KEY", err)

    def test_a_short_secret_key_is_refused(self):
        code, _, _ = load_production_settings(**{**GOOD_ENV, "SECRET_KEY": "short"})
        self.assertNotEqual(code, 0)

    def test_allowed_hosts_must_be_configured(self):
        code, _, err = load_production_settings(**{k: v for k, v in GOOD_ENV.items() if k != "ALLOWED_HOSTS"})
        self.assertNotEqual(code, 0)
        self.assertIn("ALLOWED_HOSTS", err)

    def test_the_database_password_must_be_configured(self):
        code, _, _ = load_production_settings(**{k: v for k, v in GOOD_ENV.items() if k != "POSTGRES_PASSWORD"})
        self.assertNotEqual(code, 0)

    def test_a_proper_configuration_is_hardened(self):
        code, out, err = load_production_settings(**GOOD_ENV)
        self.assertEqual(code, 0, err)
        loaded = json.loads(out.strip().splitlines()[-1])
        self.assertFalse(loaded["debug"])
        self.assertEqual(loaded["hosts"], ["staymatch.example"])
        self.assertTrue(loaded["session_secure"])
        self.assertTrue(loaded["csrf_secure"])
        self.assertGreaterEqual(loaded["hsts"], 31536000)
        self.assertEqual(loaded["proxies"], 1)
        self.assertFalse(loaded["cors_all"])
        self.assertEqual(loaded["cors"], [])
        self.assertEqual(loaded["proxy_header"], ["HTTP_X_FORWARDED_PROTO", "https"])

    def test_servers_start_with_production_settings_unless_told_otherwise(self):
        for name in ("wsgi.py", "asgi.py"):
            text = (CORE_API / "config" / name).read_text()
            self.assertIn("config.settings.production", text, name)
            self.assertNotIn("config.settings.development", text, name)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class TokenLifecycleTests(APITestCase):
    COOKIE = "staymatch_refresh"

    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com", username="member", password="Sup3rSecret!pass", role="TENANT")

    def login(self):
        response = self.client.post("/api/v1/users/login/", {"email": "member@example.com", "password": "Sup3rSecret!pass"})
        self.assertEqual(response.status_code, 200)
        return response

    def set_cookie(self, value):
        self.client.cookies[self.COOKIE] = value

    def test_access_tokens_are_short_lived(self):
        self.assertLessEqual(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"], timedelta(minutes=15))

    def test_the_refresh_token_is_only_ever_in_an_httponly_cookie(self):
        response = self.login()
        self.assertNotIn("refresh", response.data)
        self.assertIn("access", response.data)
        cookie = response.cookies[self.COOKIE]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Strict")
        self.assertEqual(cookie["path"], "/api/v1/users/")
        self.assertGreater(len(cookie.value), 50)

    def test_the_refresh_endpoint_uses_the_cookie_and_rotates_it(self):
        first = self.login().cookies[self.COOKIE].value
        response = self.client.post("/api/v1/users/token/refresh/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        rotated = response.cookies[self.COOKIE]
        self.assertTrue(rotated["httponly"])
        self.assertNotEqual(rotated.value, first)

    def test_a_refresh_token_can_only_be_used_once(self):
        first = self.login().cookies[self.COOKIE].value
        self.assertEqual(self.client.post("/api/v1/users/token/refresh/").status_code, 200)
        self.set_cookie(first)  # replay the old one
        self.assertEqual(self.client.post("/api/v1/users/token/refresh/").status_code, 401)

    def test_refreshing_without_the_cookie_fails(self):
        self.assertEqual(self.client.post("/api/v1/users/token/refresh/").status_code, 401)

    def test_a_refresh_token_in_the_request_body_is_ignored(self):
        first = self.login().cookies[self.COOKIE].value
        self.client.cookies.clear()
        response = self.client.post("/api/v1/users/token/refresh/", {"refresh": first})
        self.assertEqual(response.status_code, 401)

    def test_a_bad_cookie_is_rejected_and_cleared(self):
        self.set_cookie("not-a-token")
        response = self.client.post("/api/v1/users/token/refresh/")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.cookies[self.COOKIE].value, "")

    def test_an_access_token_cannot_be_used_as_a_refresh_token(self):
        access = self.login().data["access"]
        self.set_cookie(access)
        self.assertEqual(self.client.post("/api/v1/users/token/refresh/").status_code, 401)

    def test_logout_makes_the_refresh_token_useless_and_clears_the_cookie(self):
        value = self.login().cookies[self.COOKIE].value
        response = self.client.post("/api/v1/users/logout/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.cookies[self.COOKIE].value, "")
        self.set_cookie(value)
        self.assertEqual(self.client.post("/api/v1/users/token/refresh/").status_code, 401)

    def test_logout_without_a_session_still_succeeds(self):
        self.assertEqual(self.client.post("/api/v1/users/logout/").status_code, 204)
        self.set_cookie("junk")
        self.assertEqual(self.client.post("/api/v1/users/logout/").status_code, 204)

    def test_the_refresh_cookie_is_https_only_in_production(self):
        code, out, err = load_production_settings(**GOOD_ENV)
        self.assertEqual(code, 0, err)
        self.assertTrue(json.loads(out.strip().splitlines()[-1])["refresh_secure"])


class ListingCacheTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.landlord = User.objects.create_user(
            email="owner@example.com", username="owner", password="Sup3rSecret!pass", role="LANDLORD")

    def make(self, title="Flat"):
        return {"title": title, "description": "d", "address": "a", "city": "Pune", "state": "MH",
                "zip_code": "1", "price": "1000", "bedrooms": 1}

    def titles(self):
        return [r["title"] for r in self.client.get("/api/v1/listings/").data["results"]]

    def test_new_listings_show_up_immediately(self):
        self.assertEqual(self.titles(), [])
        self.client.force_authenticate(self.landlord)
        self.assertEqual(self.client.post("/api/v1/listings/", self.make("Studio"), format="json").status_code, 201)
        self.assertEqual(self.titles(), ["Studio"])

    def test_edits_and_deletes_show_up_immediately(self):
        listing = Listing.objects.create(owner=self.landlord, **self.make("Old"))
        self.assertEqual(self.titles(), ["Old"])
        self.client.force_authenticate(self.landlord)
        self.client.patch(f"/api/v1/listings/{listing.id}/", {"title": "New"}, format="json")
        self.assertEqual(self.titles(), ["New"])
        self.client.delete(f"/api/v1/listings/{listing.id}/")
        self.assertEqual(self.titles(), [])

    def test_a_listing_change_does_not_flush_the_rest_of_the_cache(self):
        cache.set("unrelated", "keep me", 300)
        self.client.force_authenticate(self.landlord)
        self.client.post("/api/v1/listings/", self.make(), format="json")
        self.assertEqual(cache.get("unrelated"), "keep me")

    def test_sessions_are_not_stored_only_in_the_cache(self):
        self.assertEqual(settings.SESSION_ENGINE, "django.contrib.sessions.backends.cached_db")

    def test_different_filters_get_different_cache_entries(self):
        Listing.objects.create(owner=self.landlord, **{**self.make("Pune flat")})
        Listing.objects.create(owner=self.landlord, **{**self.make("Delhi flat"), "city": "Delhi"})
        self.assertEqual(len(self.client.get("/api/v1/listings/?city=Pune").data["results"]), 1)
        self.assertEqual(len(self.client.get("/api/v1/listings/?city=Delhi").data["results"]), 1)
        self.assertEqual(len(self.client.get("/api/v1/listings/").data["results"]), 2)
