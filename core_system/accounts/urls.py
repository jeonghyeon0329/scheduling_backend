from django.urls import path
from .views import SignupProxyView, PasswordResetRequestView

app_name = "accounts"

urlpatterns = [
    path('signup/', SignupProxyView.as_view(), name='signup'),
    path('reset-password/', PasswordResetRequestView.as_view(), name='reset-password'),
]