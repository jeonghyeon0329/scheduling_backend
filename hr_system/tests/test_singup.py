import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_signup_creates_user():

    client = APIClient()
    res = client.post("/api/v1/signup/", {
        "email": "hr@test.com",
        "password": "abcd",
        "name": "tester"
    }, format="json")

    assert res.status_code == 201
    assert res.data["email"] == "hr@test.com"

    user = User.objects.filter(email="hr@test.com").first()
    assert user is not None
    assert user.is_active is True
