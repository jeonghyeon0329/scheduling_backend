from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupRequestSerializer, SignupResponseSerializer

User = get_user_model()

def _make_username(email: str) -> str:
    base = email.split("@")[0][:20] or "user"
    return f"{base}_{get_random_string(6)}"

class SignupView(APIView):
     
    @transaction.atomic
    def post(self, request):
        s = SignupRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        created = False
        user = User.objects.filter(email=d["email"]).first()
        if not user:
            user = User(
                username=_make_username(d["email"]),
                email=d["email"],
                first_name=d.get("name", ""),
                password=make_password(d["password"]),
                is_active=True,
            )
            user.save()
            created = True
   
        resp = {
            "user_id": str(user.pk), ## 분산 데이터베이스 공통 id
            "email": user.email,
            "status": "active" if user.is_active else "pending",
        }
        out = SignupResponseSerializer(resp).data
        return Response(out, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class LoginView(APIView):
    
    """로그인"""
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {
                    "detail": "이메일 또는 비밀번호가 잘못되었습니다.",
                    "code": "information wrong",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "user_id": str(user.pk),
                "email": user.email,
                "status": "active" if user.is_active else "inactive",
            },
            status=status.HTTP_200_OK,
        )
