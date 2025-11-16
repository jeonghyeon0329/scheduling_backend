from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from accounts.models import ExternalUser, ExternalUserStatus
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


class SignupInputSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=30,
        min_length=4,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9_]+$',
            message='username may only contain english letters, numbers, and underscores.'
        )]
    )
    name = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, v: str):
        v = v.strip()
        return v.lower()

    def validate(self, attrs):
        user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
        )

        password = attrs.get("password")
        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return attrs

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        for k in ('username', 'name', 'email'):
            data[k] = data[k].strip()
        return data


class ExternalUserInputSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True)
    status = serializers.ChoiceField(
        choices=ExternalUserStatus.choices,
        default=ExternalUserStatus.PENDING
    )

    def validate(self, attrs):
        if attrs.get("status") not in dict(ExternalUserStatus.choices):
            attrs["status"] = ExternalUserStatus.PENDING
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)

    def validate(self, attrs):
        uidb64 = attrs.get("uid")
        password = attrs.get("password")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = ExternalUser.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError({"password": "The link has expired."})

        try:
            validate_password(password, user=user)
        except Exception as e:
            raise serializers.ValidationError({"password": e.messages})
        
        return attrs
