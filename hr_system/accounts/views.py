from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username", "").strip().lower()
        email    = request.data.get("email", "").strip()
        name     = request.data.get("name", "").strip()
        password = request.data.get("password")

        if not all([username, email, name, password]):
            return Response({"detail": "필수값 누락"}, status=400)

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({"detail": "중복 사용자"}, status=status.HTTP_409_CONFLICT)

        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        refresh = RefreshToken.for_user(user)

        return Response({
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "status": "created"
        }, status=status.HTTP_201_CREATED)
