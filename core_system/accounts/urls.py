from django.urls import path
from .views import SignupProxyView

app_name = "accounts"

urlpatterns = [
    path('signup/', SignupProxyView.as_view(), name='signup'),
]