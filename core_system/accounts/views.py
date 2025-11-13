from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework import status
from client import hr_post
from .serializers import SignupInputSerializer, ExternalUserInputSerializer
from .models import ExternalUser
from utils.response import success_response, error_response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model


token_generator = PasswordResetTokenGenerator()
User = get_user_model()

class SignupProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupInputSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = next(
                iter(next(iter(serializer.errors.values()))))

            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code = 'CS_A1',
                message = error_message
            )
        
        payload = serializer.validated_data
        username = payload["username"]
        email = payload["email"]

        if ExternalUser.objects.filter(username=username).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="CS_A2",
                message="Username is already taken.",
            )

        if ExternalUser.objects.filter(email=email).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="CS_A2",
                message="Email is already taken.",
            )

        hr_status, hr_data = hr_post("/accounts/signup/", payload)
        
        if not hr_data.get("success", False):
            return error_response(
                status_code=hr_status,
                code=hr_data.get("code"),
                message=hr_data.get("detail"),
            )

        serializer = ExternalUserInputSerializer(data=hr_data.get("data"))
        if not serializer.is_valid():
            error_message = next(
                iter(next(iter(serializer.errors.values()))))
            
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="CS_A3",
                message=error_message
            )

        validated_data = serializer.validated_data

        try:
            with transaction.atomic():
                ExternalUser.objects.update_or_create(
                    external_user_id=validated_data["user_id"],
                    defaults={
                        "username": validated_data["username"],
                        "name": validated_data["name"],
                        "email": validated_data["email"],
                        "status": validated_data["status"],
                    },
                )
        except IntegrityError:
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="CS_A4",
                message="CR Database integrity Error."
            )

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="회원가입이 완료되었습니다.",
            data={
                "username": validated_data["username"],
                "email": validated_data["email"],
                "name": validated_data["name"],
                "status": validated_data["status"]
            }
        )
    

class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="CS_PW1",
                message="Email is required."
            )

        hr_status, hr_data = hr_post("/accounts/password/reset/request/",
            {"email": email}
        )

        # hr_system 응답 실패 시
        if not hr_data.get("success", False):
            return error_response(
                status_code=hr_status,
                code=hr_data.get("code", "CS_PW2"),
                message=hr_data.get("detail", "Password reset failed."),
            )

        # 정상 응답 시
        return success_response(
            status_code=status.HTTP_200_OK,
            message="If the email exists, a reset link was sent.",
            data={}
        )