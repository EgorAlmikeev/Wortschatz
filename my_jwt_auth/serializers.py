from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
