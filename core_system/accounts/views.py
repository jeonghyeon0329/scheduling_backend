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
        name = payload["name"]

        for field, value in [("username", username), ("email", email)]:
            user = ExternalUser.objects.filter(**{field: value}).first()
            if not user:
                continue

            if user.status != ExternalUserStatus.ACTIVE:
                return error_response(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"비활성화된 계정입니다.",
                    part="CORE_SYSTEM",
                    errors={}
                )
            
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"이미 사용 중인 {field}입니다.",
                part="CORE_SYSTEM",
                errors={field: value}
            )

        hr_status, hr_data = hr_post("/accounts/signup/", payload)
        if not hr_data.get("success", False):
            return error_response(
                status_code=hr_status,
                detail=hr_data.get("detail", "HR 시스템 회원가입 실패"),
                part="HR_SYSTEM",
                errors={},
            )
        
        user_data = hr_data.get("data") or {}
        if not isinstance(user_data, dict):
            return error_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="HR 응답 형식이 올바르지 않습니다. (data 누락)",
                part="HR_SYSTEM",
                errors={},
            )

        user_id = user_data.get("user_id")
        if not user_id:
            return error_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="HR 응답 형식이 올바르지 않습니다. (일부 누락)",
                part="HR_SYSTEM",
                errors={},
            )
        
        try:
            with transaction.atomic():
                ExternalUser.objects.update_or_create(
                    external_user_id=user_id,
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