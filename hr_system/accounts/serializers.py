from rest_framework import serializers

class SignupInputSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    name = serializers.CharField(required=True, allow_blank=False)
    email = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)

class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True, allow_blank=False)
    token = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)