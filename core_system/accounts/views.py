# accounts/views.py
from django.contrib.auth import get_user_model, login, logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db import transaction, DataError
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .serializers import SignupRequestSerializer, ExternalUserSerializer
from .models import ExternalUser
from . import hr_client



User = get_user_model()

class SignupView(views.APIView):

    """회원가입"""
    @transaction.atomic
    def post(self, request):
        s = SignupRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        email_in = d["email"].strip().lower()
        if ExternalUser.objects.filter(email=email_in).exists():
            return Response(
                {
                    "detail": "이미 사용 중인 이메일 주소입니다.",
                    "code": "email_conflict",
                    "part": "CORE_SYSTEM",
                },
                status=status.HTTP_409_CONFLICT,
            )
        
        try:
            hr_status_code, hr_res = hr_client.hr_signup(email_in, d["password"], d.get("name"))
        except Exception:
            return Response(
                {
                    "detail": "HR 서비스와 통신할 수 없습니다.",
                    "code": "hr_unreachable",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        hr_uid   = str(hr_res["user_id"])
        hr_email = (hr_res.get("email") or email_in).lower()
        hr_status= hr_res.get("status")

        if hr_status_code == 200:
            with transaction.atomic():
                obj, _ = ExternalUser.objects.update_or_create(
                    external_user_id=hr_uid,
                    defaults={
                        "email": hr_email,
                        "status": hr_status,
                    },
                )
            return Response(
                {
                    "detail": "이미 가입된 사용자 계정입니다.",
                    "code": "user_exists",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_409_CONFLICT,
            )

        elif hr_status_code == 201:
            try:
                with transaction.atomic():
                    obj, _ = ExternalUser.objects.update_or_create(
                        external_user_id=hr_uid,
                        defaults={
                            "email": hr_email,
                            "status": hr_status,
                        },
                    )
            except (ValueError, DataError) as e:
               return Response(
                    {
                        "detail": "Core DB 매핑 처리 중 오류가 발생했습니다.",
                        "code": "core_mapping_error",
                        "part": "CORE_SYSTEM"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                ExternalUserSerializer(obj).data, status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {
                    "detail": "HR 시스템이 예상치 못한 응답을 반환했습니다.",
                    "code": "hr_unexpected_response",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        
class LoginView(views.APIView):

    """로그인"""
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "detail": "이메일과 비밀번호를 입력해주세요.",
                    "code": "email or password missing",
                    "part": "CORE_SYSTEM",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            hr_status, hr_res = hr_client.hr_login(email, password)
        except Exception:
            return Response(
                {
                    "detail": "HR 서비스와 통신할 수 없습니다.",
                    "code": "hr_unreachable",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if hr_status == 401:
            return Response(
                {
                    "detail": "이메일 또는 비밀번호가 잘못되었습니다.",
                    "code": "authentication_failed",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )  
        
        elif hr_status >= 400:
            return Response(
                {
                    "detail": "HR 시스템이 예상치 못한 응답을 반환했습니다.",
                    "code": "hr_unexpected_response",
                    "part": "HR_SYSTEM",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            ) 

        external_user, _ = ExternalUser.objects.update_or_create(
            email=hr_res["email"],
            defaults={
                "status": hr_res.get("status", "active"),
                "updated_at": timezone.now(),
            },
        )

        user, _ = User.objects.get_or_create(
            email=hr_res["email"], defaults={"is_active": True}
        )

        # 인증 없이 강제로 로그인 처리 (백엔드 지정)
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

        return Response(
            {
                "detail": "로그인 성공",
                "user_id": str(external_user.external_user_id),
                "email": hr_res["email"],
            },
            status=status.HTTP_200_OK,
        )
    

@method_decorator(csrf_protect, name="dispatch") 
class LogoutView(views.APIView):
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    
    """로그아웃"""
    def post(self, request):
        """
            X-CSRFToken : Header : csrftoken 쿠키값
            csrftoken : cookies : csrftoken 쿠키값
            sessionid : cookies : sessionid 쿠키값
        """
        logout(request)
        return Response(
            {
                "detail": "로그아웃 완료"
            },
            status=status.HTTP_200_OK
        )


class ForceLogoutView(views.APIView):

    """강제 로그아웃"""
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {
                    "detail": "email 정보를 확인할 수 없습니다.",
                    "code": "invalid_request",
                    "part": "CORE_SYSTEM",
                },
                status=status.HTTP_400_BAD_REQUEST,
            ) 

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response(
                {
                    "detail": "회원가입이 완료된 이메일이 아닙니다.",
                    "code": "user_not_found",
                    "part": "CORE_SYSTEM",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        count = 0
        for session in sessions:
            data = session.get_decoded()
            if data.get("_auth_user_id") == str(user.pk):
                session.delete()
                count += 1

        return Response(
            {
                "detail": f"{email} 강제 로그아웃 완료",
                "terminated_sessions": count,
            },
            status=status.HTTP_200_OK,
        )