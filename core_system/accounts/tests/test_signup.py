from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from accounts.models import ExternalUser
import uuid


class SignupProxyTests(APITestCase):

    def setUp(self):
        self.url = reverse("accounts:signup")
        self.payload = {
            "username": "testuser",
            "email": "test@test.com",
            "name": "테스트",
            "password": "Abcde12345!"
        }
        self.uuid_str = str(uuid.uuid4())

    @patch("accounts.views.hr_post")
    def test_signup_success(self, mock_hr_post):
        """정상 회원가입 (201)"""

        mock_hr_post.return_value = (
            201,
            {
                "success": True,
                "data": {
                    "user_id": self.uuid_str,
                    "username": "testuser",
                    "email": "test@test.com",
                    "name": "테스트",
                    "status": "active"
                }
            }
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "testuser")
        self.assertTrue(ExternalUser.objects.filter(username="testuser").exists())

    def test_signup_invalid_payload(self):
        """입력값 validation 실패 → 400 (CS_A1)"""

        invalid_data = {
            "username": "testuser"
        }

        response = self.client.post(self.url, invalid_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "CS_A1")

    @patch("accounts.views.hr_post")
    def test_username_duplicate(self, mock_hr_post):
        """username 중복 → 409 (CS_A2)"""

        ExternalUser.objects.create(
            external_user_id=str(uuid.uuid4()),
            username="testuser",
            email="hello@world.com",
            name="기존유저",
            status="active"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "CS_A2")

    @patch("accounts.views.hr_post")
    def test_email_duplicate(self, mock_hr_post):
        """email 중복 → 409 (CS_A2)"""

        ExternalUser.objects.create(
            external_user_id=str(uuid.uuid4()),
            username="otheruser",
            email="test@test.com",
            name="기존유저",
            status="active"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "CS_A2")

    @patch("accounts.views.hr_post")
    def test_hr_system_error(self, mock_hr_post):
        """hr_system에서 실패 응답 → core_system이 그대로 반환"""

        mock_hr_post.return_value = (
            400,
            {
                "success": False,
                "code": "HR_TEST_1",
                "detail": "HR Error"
            }
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "HR_TEST_1")

    @patch("accounts.views.hr_post")
    def test_hr_response_validation_error(self, mock_hr_post):
        """hr_system 응답 데이터 validation 실패 → 400 (CS_A3)"""

        mock_hr_post.return_value = (
            201,
            {
                "success": True,
                "data": {
                    # username 누락
                    "user_id": str(uuid.uuid4()),
                    "email": "test@test.com",
                    "name": "테스트",
                    "status": "active"
                }
            }
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "CS_A3")

    @patch("accounts.views.hr_post")
    @patch("accounts.views.ExternalUser.objects.update_or_create")
    def test_integrity_error(self, mock_update_or_create, mock_hr_post):
        """IntegrityError 발생 → 409 (CS_A4)"""

        mock_hr_post.return_value = (
            201,
            {
                "success": True,
                "data": {
                    "user_id": str(uuid.uuid4()),
                    "username": "testuser",
                    "email": "test@test.com",
                    "name": "테스트",
                    "status": "active"
                }
            }
        )

        from django.db import IntegrityError
        mock_update_or_create.side_effect = IntegrityError()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "CS_A4")
