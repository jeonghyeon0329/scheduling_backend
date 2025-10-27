import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.models import ExternalUser

User = get_user_model()

@pytest.mark.django_db
def test_login_and_external_user_created():

    # User.objects.create_user(email="core@test.com", password="1234")

    client = APIClient()
    res = client.post("/api/accounts/login/", {
        "email": "test@test.com",
        "password": "test"
    }, format="json")

    assert res.status_code == 200
    assert res.data["email"] == "test@test.com"

    external_user = ExternalUser.objects.filter(email="test@test.com").first()
    assert external_user is not None
    assert external_user.status == "active"
