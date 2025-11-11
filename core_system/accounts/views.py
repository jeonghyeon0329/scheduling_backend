from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework import status
from client import hr_post
from .serializers import SignupInputSerializer
from .models import ExternalUser, ExternalUserStatus
from utils.response import success_response, error_response


class SignupProxyView(APIView):
    authentication_classes = []
    permission_classes = []
    FIELD_LABELS = {
        "username": "아이디", 
        "email": "이메일", 
        "password": "비밀번호", 
        "name": "이름"
    }

    def post(self, request):
        serializer = SignupInputSerializer(data=request.data)
        if not serializer.is_valid():
            field, messages = next(iter(serializer.errors.items()))
            label = self.FIELD_LABELS.get(field, field)
            priori_message = messages[0] if isinstance(messages, list) else str(messages)
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{priori_message}",
                part="CORE_SYSTEM",
                errors=serializer.errors
            )
        
        payload = serializer.validated_data
        username = payload["username"]
        email = payload["email"]
        name = payload["name"]

        unique_field = {
            "username": ("아이디", username),
            "email": ("이메일", email),
        }
        for db_field, (label, value) in unique_field.items():
            if not value:
                continue

            user = ExternalUser.objects.filter(**{db_field: value}).first()
            if user:
                return error_response(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"이미 사용 중인 {label}입니다.",
                    part="CORE_SYSTEM",
                    errors={label: value}
                )

        hr_status, hr_data = hr_post("/accounts/signup/", payload)
        checks = [
            ("HR 회원가입 응답 실패", not hr_data.get("success", False)),
            ("HR 회원가입 data 필드 타입 오류", not isinstance(hr_data.get("data"), dict)),
            ("HR 회원가입 user_id 누락", not hr_data.get("data", {}).get("user_id")),
        ]

        for log_msg, condition in checks:
            if condition:
                # logger.error("[HR_SYSTEM ERROR] %s | status=%s | data=%s", log_msg, hr_status, hr_data)
                return error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="내부 시스템 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    part="HR_SYSTEM",
                    errors={log_msg},
                )
        
        user_data = hr_data.get("data")
        try:
            with transaction.atomic():
                ExternalUser.objects.update_or_create(
                    external_user_id=user_data.get("user_id"),
                    defaults={
                        "username": user_data.get("username", username),
                        "name": user_data.get("name", name),
                        "email": user_data.get("email", email),
                        "status": user_data.get("status", ExternalUserStatus.PENDING),
                    },
                )
        except IntegrityError:
            ## 동시 요청을 진행하는 경우 무결성 오류
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                detail="처리지연이 발생하고 있습니다. 잠시후 다시 시도해주시기 바랍니다.",
                part="CORE_SYSTEM",
                errors={},
            )


        allowed_fields = ["username", "email", "name", "status"]
        filtered_data = {k: v for k, v in user_data.items() if k in allowed_fields}

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="회원가입이 완료되었습니다.",
            data=filtered_data,
        )