from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SignupInputSerializer
from utils.response import success_response, error_response

User = get_user_model()

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
