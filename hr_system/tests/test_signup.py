from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.db import IntegrityError
import uuid

User = get_user_model()


class HrSignupViewTests(APITestCase):

    def setUp(self):
        self.url = reverse("accounts:signup")  # hr_system URL
        self.payload = {
            "username": "testuser",
            "email": "test@test.com",
            "name": "테스트",
            "password": "Abcde12345!"
        }

    def test_signup_success(self):
        """test1: 정상 회원가입 → 201"""

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "testuser")

        # DB 저장 확인
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_invalid_payload(self):
        """test2: 입력값 validation 실패 → 400 (HS_A1)"""

        invalid_data = {"username": "abc"}

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "HS_A1")

    def test_username_duplicate(self):
        """test3: username 중복 → 409 (HS_A2)"""

        # 기존 사용자 생성
        User.objects.create_user(
            username="testuser",
            email="other@test.com",
            password="Test1234!",
            first_name="기존유저"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "HS_A2")

    def test_email_duplicate(self):
        """test4: email 중복 → 409 (HS_A2)"""

        User.objects.create_user(
            username="otheruser",
            email="test@test.com",
            password="Test1234!",
            first_name="기존유저"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "HS_A2")

    @patch("accounts.views.User.objects.create_user")
    def test_integrity_error(self, mock_create_user):
        """test5: DB IntegrityError → 409 (HS_A3)"""

        mock_create_user.side_effect = IntegrityError()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "HS_A3")

    def test_whitespace_trim(self):
        """test7: 입력값 공백이 제거되는지 확인"""

        payload = {
            "username": " testuser ",
            "email": " test@test.com ",
            "name": " 테스트 ",
            "password": "Abcde12345!",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"]["username"], "testuser")
