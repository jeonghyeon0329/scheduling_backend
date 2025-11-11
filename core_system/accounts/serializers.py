from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class SignupInputSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=30,
        min_length=4,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9_]+$',
            message='username은 영문/숫자만 사용할 수 있습니다.'
        )]
    )
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=254)

    """
    <p className="password-rules">
        비밀번호 규칙:
        <ul>
            <li>8자 이상 입력해야 합니다</li>
            <li>숫자만으로 구성할 수 없습니다</li>
            <li>너무 흔한 비밀번호는 사용할 수 없습니다</li>
            <li>사용자 이름 또는 이메일과 유사할 수 없습니다</li>
        </ul>
    </p>    
    """
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, v: str):
        v = v.strip()
        if v != v.lower():
            return v.lower()
        return v

    def validate_password(self, v: str):
        try:
            validate_password(v)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return v

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        for k in ('username', 'name', 'email'):
            data[k] = data[k].strip()
        return data
