from django.urls import path
from .views import SignupView, PasswordResetRequestView

app_name = "accounts"

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('reset-password/', PasswordResetRequestView.as_view(), name='reset-password'),
]
