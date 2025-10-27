# accounts/serializers.py
from rest_framework import serializers

class SignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)
    name = serializers.CharField(max_length=100)

class SignupResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    email = serializers.EmailField()
    status = serializers.CharField()
