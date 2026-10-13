from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("users:register")
        self.valid_data = {
            "username": "taskflow_test_user",
            "email": "taskflow_test@example.com",
            "password": "TaskFlowTest2026!Strong",
            "password2": "TaskFlowTest2026!Strong",
        }

    def test_register_success(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(User.objects.filter(username="taskflow_test_user").exists())

    def test_passwords_do_not_match(self):
        data = self.valid_data.copy()
        data["password2"] = "DifferentPassword2026!"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(User.objects.count(), 0)

    def test_weak_password_rejected(self):
        data = self.valid_data.copy()
        data["password"] = "123456"
        data["password2"] = "123456"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_username_rejected(self):
        User.objects.create_user(
            username="taskflow_test_user",
            password="ExistingUser2026!Strong",
        )

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(User.objects.count(), 1)

    def test_password_not_returned(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertNotIn("password", response.data)
        self.assertNotIn("password2", response.data)

    def test_password_is_hashed(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(username="taskflow_test_user")

        self.assertNotEqual(
            user.password,
            self.valid_data["password"],
        )
        self.assertTrue(user.check_password(self.valid_data["password"]))


class JWTAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="jwt_test_user",
            password="JWTTest2026!Strong",
        )

        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")

    def test_obtain_token_success(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "jwt_test_user",
                "password": "JWTTest2026!Strong",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_wrong_password(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "jwt_test_user",
                "password": "WrongPassword2026!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_refresh_access_token(self):
        login_response = self.client.post(
            self.token_url,
            {
                "username": "jwt_test_user",
                "password": "JWTTest2026!Strong",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
