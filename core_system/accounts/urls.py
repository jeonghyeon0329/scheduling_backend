from django.urls import path
from .views import SignupProxyView, LoginProxyView, PasswordResetRequestView, PasswordResetConfirmProxyView

app_name = "accounts"

urlpatterns = [
    path('signup/', SignupProxyView.as_view(), name='signup'),
    path('login/', LoginProxyView.as_view(), name='login'),
    path('forgot-password/', PasswordResetRequestView.as_view(), name='forgot-password'),
    path('reset-password/', PasswordResetConfirmProxyView.as_view(), name='reset-password'),
]
