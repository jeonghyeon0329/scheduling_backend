# accounts/serializers.py
from rest_framework import serializers
from .models import ExternalUser

class SignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)
    name = serializers.CharField(max_length=100)

class ExternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalUser
        fields = ("external_user_id", "email", "status", "updated_at")
        read_only_fields = fields
