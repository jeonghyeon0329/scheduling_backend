from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password

class SignupInputSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=30,
        min_length=4,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9_.-]+$',
            message='username은 영문/숫자/._- 만 사용할 수 있습니다.'
        )]
    )
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, v: str):
        v = v.strip()
        if v != v.lower():
            return v.lower()
        return v

    def validate_password(self, v: str):
        validate_password(v)
        return v

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        for k in ('username', 'name', 'email'):
            data[k] = data[k].strip()
        return data
