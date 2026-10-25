
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.me_url = reverse("me")
        self.logout_url = reverse("logout")
        self.change_password_url = reverse("change-password")

        self.password = "S3cure-Long-Passphrase-928!"

    def register_data(self, **overrides):
        data = {
            "username": "candidate_test",
            "email": "candidate@example.com",
            "password": self.password,
            "password2": self.password,
            "role": "CANDIDATE",
        }
        data.update(overrides)
        return data

    def create_user(self, **overrides):
        data = {
            "username": "existing_user",
            "email": "existing@example.com",
            "password": self.password,
            "role": "CANDIDATE",
        }
        data.update(overrides)
        return User.objects.create_user(**data)

    def login_and_get_tokens(self, username="existing_user"):
        response = self.client.post(
            self.login_url,
            {
                "username": username,
                "password": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data

    def authenticate(self, access_token):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    # 1. Registration succeeds and does not expose passwords.
    def test_register_candidate(self):
        response = self.client.post(
            self.register_url,
            self.register_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertNotIn("password", response.data)
        self.assertNotIn("password2", response.data)
        self.assertTrue(
            User.objects.filter(
                email="candidate@example.com"
            ).exists()
        )

    # 2. Public registration cannot create an admin.
    def test_register_admin_fails(self):
        response = self.client.post(
            self.register_url,
            self.register_data(role="ADMIN"),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # 3. Duplicate emails are rejected case-insensitively.
    def test_duplicate_email_different_case_fails(self):
        self.create_user(email="Admin@gmail.com")

        response = self.client.post(
            self.register_url,
            self.register_data(email="admin@gmail.com"),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # 4. Password confirmation must match.
    def test_mismatched_passwords_fail(self):
        response = self.client.post(
            self.register_url,
            self.register_data(
                password2="Different-Secure-Password-928!"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # 5. Login returns both JWT tokens.
    def test_login_returns_access_and_refresh(self):
        self.create_user()

        tokens = self.login_and_get_tokens()

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    # 6. /me/ rejects unauthenticated requests.
    def test_me_without_token_returns_401(self):
        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # 7. /me/ accepts a valid access token.
    def test_me_with_token_returns_200(self):
        self.create_user()
        tokens = self.login_and_get_tokens()

        self.authenticate(tokens["access"])
        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["username"], "existing_user")

    # 8. A blacklisted refresh token cannot be used again.
    def test_logout_then_refresh_returns_401(self):
        self.create_user()
        tokens = self.login_and_get_tokens()

        self.authenticate(tokens["access"])
        logout_response = self.client.post(
            self.logout_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_205_RESET_CONTENT,
        )

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # 9. An incorrect old password must be rejected.
    def test_change_password_wrong_old_password_fails(self):
        self.create_user()
        tokens = self.login_and_get_tokens()

        self.authenticate(tokens["access"])
        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "Wrong-Old-Password-928!",
                "new_password": "Another-Secure-Password-837!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
