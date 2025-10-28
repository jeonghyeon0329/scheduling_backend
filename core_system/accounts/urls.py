# accounts/urls.py
from django.urls import path
from django.http import HttpResponse

from .views import SignupView, LoginView, LogoutView, ForceLogoutView


def health(request):
    return HttpResponse("ok")

app_name = "accounts"
urlpatterns = [
    path("health/", health, name="health"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("force-logout/", ForceLogoutView.as_view(), name="force_logout"),
]