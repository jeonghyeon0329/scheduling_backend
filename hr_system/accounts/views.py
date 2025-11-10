from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import status
from utils.response import success_response, error_response

User = get_user_model()

class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username", "").strip().lower()
        email    = request.data.get("email", "").strip().lower()
        name     = request.data.get("name", "").strip()
        password = request.data.get("password")

        if not all([username, email, name, password]):
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="필수값이 누락되었습니다.",
                part="HR_SYSTEM",
                errors={"missing_fields": [k for k, v in {
                    "username": username, "email": email, "name": name, "password": password
                }.items() if not v]}
            )

        try:
            validate_email(email)
        except ValidationError:
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일 형식이 올바르지 않습니다.",
                part="HR_SYSTEM",
                errors={"email": email}
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 정책을 위반했습니다.",
                part="HR_SYSTEM",
                errors={"password": e.messages}
            )

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 사용자입니다.",
                part="HR_SYSTEM",
                errors={"username": username, "email": email}
            )

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name
            )
        except IntegrityError:
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                detail="중복 사용자로 인해 생성 실패",
                part="HR_SYSTEM",
                errors={"username": username}
            )

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="회원가입이 완료되었습니다.",
            data={
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "name": user.first_name,
                "status": "active",
            }
        )
