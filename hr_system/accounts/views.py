from django.contrib.auth import get_user_model, authenticate, login
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SignupInputSerializer, LoginSerializer, PasswordResetSerializer
from utils.response import success_response, error_response
from utils.threading import send_reset_email_async
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupInputSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = next(
                iter(next(iter(serializer.errors.values()))))

            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code = 'HS_A1',
                message = error_message
            )

        payload = serializer.validated_data
        username = payload["username"]
        email = payload["email"]
        name = payload["name"]
        password = payload["password"]
        
        if User.objects.filter(username=username).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="HS_A2",
                message="Username is already taken.",
            )

        if User.objects.filter(email=email).exists():
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="HS_A2",
                message="Email is already taken.",
            )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name
                )

        except IntegrityError:
            return error_response(
                status_code=status.HTTP_409_CONFLICT,
                code="HS_A3",
                message="HR Database integrity Error",
            )

        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="complete signup",
            data={
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "name": user.first_name,
                "status": "active",
            }
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = next(
                iter(next(iter(serializer.errors.values()))))

            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code = 'HS_A8',
                message = error_message
            )

        payload = serializer.validated_data
        username = payload["username"]
        password = payload["password"]  

        user = authenticate(request, username=username, password=password)

        if user is None:
            return error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="HS_A9",
                message="Wrong Information or Unknown user."
            )

        login(request, user)
        refresh = RefreshToken.for_user(user)
        return success_response(
            status_code=200,
            message="Login success.",
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh)
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
                code="HS_A4",
                message="Email address is required."
            )

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            base_url = settings.FRONTEND_BASE_URL.rstrip("/")
            reset_url = f"{base_url}/reset-password?uid={uid}&token={token}"

            send_reset_email_async(
                to_email=email,
                reset_url=reset_url,
                user_name=user.first_name
            )

        except User.DoesNotExist:
            pass

        return success_response(
            status_code=status.HTTP_200_OK,
            message="If the email exists, a reset link was sent.",
            data={}
        )
    
class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = next(
                iter(next(iter(serializer.errors.values()))))

            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code = 'HS_A5',
                message = error_message
            )

        payload = serializer.validated_data
        uid = payload["uid"]
        token = payload["token"]
        password = payload["password"]
        
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except:
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code = 'HS_A6',
                message = "Invalid JSON response."
            )

        if not token_generator.check_token(user, token):
            return error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code = 'HS_A7',
                message = "The link has expired."
            )

        user.set_password(password)
        user.save()

        return success_response(
            status_code=200,
            message="Password changed successfully.",
            data={}
        )
