from rest_framework.views import APIView
from rest_framework import status
from client import hr_post
from .serializers import SignupInputSerializer
from .models import ExternalUser
from utils.response import success_response, error_response


class SignupProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupInputSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="입력값 검증 실패",
                part="CORE_SYSTEM",
                errors=serializer.errors
            )

        payload = serializer.validated_data
        username = payload["username"]
        email = payload["email"]

        if ExternalUser.objects.filter(username=username).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 사용자명입니다.",
                part="CORE_SYSTEM",
                errors={}
            )

        if ExternalUser.objects.filter(email=email).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 가입된 이메일입니다.",
                part="CORE_SYSTEM",
                errors={}
            )

        hr_status, hr_data = hr_post("/signup/", payload)

        if hr_status not in (200, 201):
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="HR 시스템 요청 실패",
                part="HR_SYSTEM",
                errors=hr_data
            )

        ExternalUser.objects.update_or_create(
            external_user_id=hr_data["user_id"],
            defaults={
                "username": hr_data.get("username", username),
                "email": hr_data.get("email", email),
                "status": hr_data.get("status", "created"),
            }
        )

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="회원가입이 완료되었습니다.",
            data=hr_data
        )
