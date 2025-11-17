from django.urls import path
from .views import SignupView, PasswordResetRequestView, PasswordResetConfirmView, LoginView

app_name = "accounts"

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', PasswordResetRequestView.as_view(), name='forgot-password'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='reset-password'),
]
