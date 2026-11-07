import base64
import hashlib
import hmac
import json
import time
from types import SimpleNamespace
from unittest import mock

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.users.models import User

SECRET = "s" * 40
OAUTH = "/api/v1/users/oauth/login/"
REGISTER = "/api/v1/users/register/"
LOGIN = "/api/v1/users/login/"
ME = "/api/v1/users/me/"


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def make_token(secret=SECRET, algorithm="HS256", **overrides):
    claims = {
        "sub": "user-123",
        "email": "newuser@example.com",
        "aud": "authenticated",
        "exp": int(time.time()) + 600,
        "user_metadata": {"email_verified": True, "full_name": "New User"},
        "app_metadata": {"provider": "google"},
    }
    claims.update(overrides)
    return jwt.encode(claims, secret, algorithm=algorithm)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])  # fast hashing, tests only
class AuthTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_user(
            email="admin@staymatch.com", username="admin", password="Sup3rSecret!pass",
            role=User.Role.ADMIN, is_staff=True, is_superuser=True,
        )
        self.tenant = User.objects.create_user(
            email="alex@staymatch.com", username="alex", password="Sup3rSecret!pass", role=User.Role.TENANT,
        )

    def me_as(self, response):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        result = self.client.get(ME)
        self.client.credentials()
        return result


@override_settings(SUPABASE_JWT_SECRET=SECRET, SUPABASE_URL="", ALLOW_INSECURE_DEMO_OAUTH=False)
class OAuthLoginTests(AuthTestCase):
    def test_valid_token_logs_in_the_matching_existing_user(self):
        response = self.client.post(OAUTH, {"id_token": make_token(email="alex@staymatch.com")}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.me_as(response).data["email"], "alex@staymatch.com")

    def test_email_alone_is_not_a_credential(self):
        response = self.client.post(OAUTH, {"email": "alex@staymatch.com"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)

    def test_unsigned_token_is_rejected(self):
        payload = b64(json.dumps({"email": "admin@staymatch.com", "sub": "x", "aud": "authenticated",
                                  "exp": int(time.time()) + 600}).encode())
        header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        forged = f"{header}.{payload}.{b64(b'bad-signature')}"
        self.assertEqual(self.client.post(OAUTH, {"id_token": forged}, format="json").status_code, 401)

    def test_alg_none_token_is_rejected(self):
        header = b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
        payload = b64(json.dumps({"email": "admin@staymatch.com", "sub": "x", "aud": "authenticated",
                                  "exp": int(time.time()) + 600}).encode())
        self.assertEqual(self.client.post(OAUTH, {"id_token": f"{header}.{payload}."}, format="json").status_code, 401)

    def test_token_signed_with_the_wrong_secret_is_rejected(self):
        token = make_token(secret="w" * 40, email="admin@staymatch.com")
        self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)

    def test_expired_token_is_rejected(self):
        token = make_token(exp=int(time.time()) - 10, email="alex@staymatch.com")
        self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)

    def test_token_for_another_audience_is_rejected(self):
        token = make_token(aud="something-else", email="alex@staymatch.com")
        self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)

    def test_unverified_email_is_rejected(self):
        token = make_token(email="alex@staymatch.com", user_metadata={"email_verified": False})
        response = self.client.post(OAUTH, {"id_token": token}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_token_without_an_email_is_rejected(self):
        token = make_token(email="")
        self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)

    def test_garbage_tokens_are_rejected(self):
        for bad in ("", "abc", "a.b", "a.b.c.d", 12345, None, ["x"]):
            payload = {"id_token": bad} if bad is not None else {}
            self.assertEqual(self.client.post(OAUTH, payload, format="json").status_code, 401, bad)

    def test_new_user_is_created_as_tenant_with_no_usable_password(self):
        response = self.client.post(OAUTH, {"id_token": make_token()}, format="json")
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email="newuser@example.com")
        self.assertEqual(user.role, User.Role.TENANT)
        self.assertFalse(user.has_usable_password())
        self.assertEqual((user.first_name, user.last_name), ("New", "User"))

    def test_new_user_may_choose_landlord_but_never_admin(self):
        self.client.post(OAUTH, {"id_token": make_token(email="l@example.com"), "role": "LANDLORD"}, format="json")
        self.client.post(OAUTH, {"id_token": make_token(email="a@example.com"), "role": "ADMIN"}, format="json")
        self.assertEqual(User.objects.get(email="l@example.com").role, User.Role.LANDLORD)
        self.assertEqual(User.objects.get(email="a@example.com").role, User.Role.TENANT)

    def test_role_parameter_cannot_change_an_existing_user(self):
        self.client.post(OAUTH, {"id_token": make_token(email="alex@staymatch.com"), "role": "ADMIN"}, format="json")
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.role, User.Role.TENANT)

    def test_username_prefix_never_maps_to_another_account(self):
        # Previously "admin@attacker.example" was matched to the existing user named "admin".
        response = self.client.post(OAUTH, {"id_token": make_token(email="admin@attacker.example")}, format="json")
        self.assertEqual(response.status_code, 200)
        me = self.me_as(response).data
        self.assertEqual(me["email"], "admin@attacker.example")
        self.assertEqual(me["role"], User.Role.TENANT)
        self.assertNotEqual(me["id"], str(self.admin.id))
        self.assertNotEqual(me["username"], "admin")

    def test_email_matching_is_case_insensitive(self):
        response = self.client.post(OAUTH, {"id_token": make_token(email="ALEX@Staymatch.com")}, format="json")
        self.assertEqual(self.me_as(response).data["email"], "alex@staymatch.com")
        self.assertEqual(User.objects.filter(email__iexact="alex@staymatch.com").count(), 1)

    def test_disabled_account_cannot_sign_in(self):
        self.tenant.is_active = False
        self.tenant.save()
        response = self.client.post(OAUTH, {"id_token": make_token(email="alex@staymatch.com")}, format="json")
        self.assertEqual(response.status_code, 403)


class AsymmetricTokenTests(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.private_pem = self.private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
        self.public_pem = self.public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def fake_jwks(self):
        return mock.patch(
            "apps.users.oauth._jwks_client",
            return_value=SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=self.public_key)),
        )

    @override_settings(SUPABASE_URL="https://proj.supabase.co", SUPABASE_JWT_SECRET="")
    def test_rs256_token_verified_with_the_project_keys(self):
        token = make_token(self.private_pem, "RS256", email="alex@staymatch.com", iss="https://proj.supabase.co/auth/v1")
        with self.fake_jwks():
            response = self.client.post(OAUTH, {"id_token": token}, format="json")
        self.assertEqual(response.status_code, 200)

    @override_settings(SUPABASE_URL="https://proj.supabase.co", SUPABASE_JWT_SECRET="")
    def test_wrong_issuer_is_rejected(self):
        token = make_token(self.private_pem, "RS256", email="alex@staymatch.com", iss="https://evil.example/auth/v1")
        with self.fake_jwks():
            self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)

    @override_settings(SUPABASE_URL="https://proj.supabase.co", SUPABASE_JWT_SECRET="")
    def test_rsa_public_key_cannot_be_used_as_an_hmac_secret(self):
        header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        payload = b64(json.dumps({"email": "admin@staymatch.com", "sub": "x", "aud": "authenticated",
                                  "exp": int(time.time()) + 600, "iss": "https://proj.supabase.co/auth/v1",
                                  "user_metadata": {"email_verified": True}}).encode())
        signature = b64(hmac.new(self.public_pem, f"{header}.{payload}".encode(), hashlib.sha256).digest())
        with self.fake_jwks():
            response = self.client.post(OAUTH, {"id_token": f"{header}.{payload}.{signature}"}, format="json")
        self.assertEqual(response.status_code, 401)

    @override_settings(SUPABASE_URL="https://proj.supabase.co", SUPABASE_JWT_SECRET="")
    def test_unreachable_key_endpoint_rejects_rather_than_trusting(self):
        token = make_token(self.private_pem, "RS256", email="alex@staymatch.com", iss="https://proj.supabase.co/auth/v1")
        boom = mock.Mock(side_effect=OSError("network down"))
        with mock.patch("apps.users.oauth._jwks_client", return_value=SimpleNamespace(get_signing_key_from_jwt=boom)):
            self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)

    @override_settings(SUPABASE_URL="", SUPABASE_JWT_SECRET="")
    def test_nothing_is_accepted_when_verification_is_not_configured(self):
        token = make_token(self.private_pem, "RS256", email="alex@staymatch.com")
        self.assertEqual(self.client.post(OAUTH, {"id_token": token}, format="json").status_code, 401)


@override_settings(SUPABASE_JWT_SECRET="", SUPABASE_URL="")
class DemoLoginTests(AuthTestCase):
    @override_settings(ALLOW_INSECURE_DEMO_OAUTH=False, DEBUG=True)
    def test_demo_login_is_off_by_default(self):
        self.assertEqual(self.client.post(OAUTH, {"email": "new@example.com"}, format="json").status_code, 401)

    @override_settings(ALLOW_INSECURE_DEMO_OAUTH=True, DEBUG=False)
    def test_demo_login_is_ignored_outside_debug(self):
        self.assertEqual(self.client.post(OAUTH, {"email": "new@example.com"}, format="json").status_code, 401)

    @override_settings(ALLOW_INSECURE_DEMO_OAUTH=True, DEBUG=True)
    def test_demo_login_creates_a_passwordless_account(self):
        response = self.client.post(OAUTH, {"email": "Demo@Example.com", "name": "Demo User"}, format="json")
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email="demo@example.com")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.role, User.Role.TENANT)

    @override_settings(ALLOW_INSECURE_DEMO_OAUTH=True, DEBUG=True)
    def test_demo_login_cannot_sign_in_to_an_account_with_a_password(self):
        for email in ("admin@staymatch.com", "alex@staymatch.com"):
            response = self.client.post(OAUTH, {"email": email}, format="json")
            self.assertEqual(response.status_code, 403, email)
            self.assertNotIn("access", response.data)

    @override_settings(ALLOW_INSECURE_DEMO_OAUTH=True, DEBUG=True)
    def test_demo_login_rejects_an_invalid_email(self):
        self.assertEqual(self.client.post(OAUTH, {"email": "not-an-email"}, format="json").status_code, 400)

    @override_settings(ALLOW_INSECURE_DEMO_OAUTH=True, DEBUG=True)
    def test_demo_login_cannot_assign_a_privileged_role(self):
        self.client.post(OAUTH, {"email": "wannabe@example.com", "role": "ADMIN"}, format="json")
        self.assertEqual(User.objects.get(email="wannabe@example.com").role, User.Role.TENANT)


class RegistrationTests(AuthTestCase):
    def payload(self, **overrides):
        data = {"email": "fresh@example.com", "username": "fresh", "password": "Tr0ub4dor&3x!", "role": "TENANT"}
        data.update(overrides)
        return data

    def test_registration_defaults_to_tenant(self):
        data = self.payload()
        del data["role"]
        self.assertEqual(self.client.post(REGISTER, data, format="json").status_code, 201)
        self.assertEqual(User.objects.get(email="fresh@example.com").role, User.Role.TENANT)

    def test_landlord_is_allowed(self):
        self.assertEqual(self.client.post(REGISTER, self.payload(role="LANDLORD"), format="json").status_code, 201)
        self.assertEqual(User.objects.get(email="fresh@example.com").role, User.Role.LANDLORD)

    def test_admin_role_is_refused(self):
        response = self.client.post(REGISTER, self.payload(role="ADMIN"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="fresh@example.com").exists())

    def test_weak_passwords_are_refused(self):
        for weak in ("x", "short1", "password", "12345678", "fresh@example.com"):
            response = self.client.post(REGISTER, self.payload(password=weak), format="json")
            self.assertEqual(response.status_code, 400, weak)
            self.assertIn("password", response.data)

    def test_duplicate_email_is_refused_regardless_of_case(self):
        response = self.client.post(REGISTER, self.payload(email="ALEX@staymatch.com"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_duplicate_username_is_refused_regardless_of_case(self):
        response = self.client.post(REGISTER, self.payload(username="ADMIN"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_email_is_stored_in_lower_case(self):
        self.client.post(REGISTER, self.payload(email="Mixed.Case@Example.com"), format="json")
        self.assertTrue(User.objects.filter(email="mixed.case@example.com").exists())

    def test_password_is_never_returned(self):
        response = self.client.post(REGISTER, self.payload(), format="json")
        self.assertNotIn("password", response.data)


class ProfileUpdateTests(AuthTestCase):
    def login(self, user):
        self.client.force_authenticate(user)

    def test_role_cannot_be_changed_through_the_profile(self):
        self.login(self.tenant)
        response = self.client.patch(ME, {"role": "ADMIN"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.role, User.Role.TENANT)
        self.assertEqual(response.data["role"], User.Role.TENANT)

    def test_email_cannot_be_changed_through_the_profile(self):
        self.login(self.tenant)
        self.client.patch(ME, {"email": "hijack@example.com"}, format="json")
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.email, "alex@staymatch.com")

    def test_contact_details_can_still_be_updated(self):
        self.login(self.tenant)
        response = self.client.patch(ME, {"phone_number": "+91 90000 00000", "bio": "Hello"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual((self.tenant.phone_number, self.tenant.bio), ("+91 90000 00000", "Hello"))

    def test_profile_requires_authentication(self):
        self.assertEqual(self.client.get(ME).status_code, 401)


class AuthThrottleTests(AuthTestCase):
    def test_repeated_failed_logins_are_rate_limited(self):
        statuses = [
            self.client.post(LOGIN, {"email": "alex@staymatch.com", "password": "wrong"}, format="json").status_code
            for _ in range(12)
        ]
        self.assertEqual(statuses[:10], [401] * 10)
        self.assertIn(429, statuses[10:])

    def test_correct_credentials_still_work(self):
        response = self.client.post(LOGIN, {"email": "alex@staymatch.com", "password": "Sup3rSecret!pass"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["role"], User.Role.TENANT)
