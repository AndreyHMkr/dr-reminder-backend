from django.contrib.auth import get_user_model
from rest_framework import serializers

from dr_reminder_api import settings


def validate_password_complexity(password: str) -> str:
    if not any(char.isupper() for char in password):
        raise serializers.ValidationError("Password must contain at least one uppercase character.")
    if not any(char.islower() for char in password):
        raise serializers.ValidationError("Password must contain at least one lowercase character.")
    if not any(char.isdigit() for char in password):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/\\\"'" for char in password):
        raise serializers.ValidationError("Password must contain at least one special character.")
    if any(ord(char) < 32 for char in password):
        raise serializers.ValidationError("Password must not contain non-printing characters.")
    return password


class UserSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password", "repeat_password", "is_staff",)
        read_only_fields = ("id", "is_staff",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 30,
                "style": {"input_type": "password"},
            },
        }

    def validate_email(self, email: str) -> str:
        if not (12 <= len(email) <= 72):
            raise serializers.ValidationError("Email must be between 12 and 72 characters.")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise serializers.ValidationError("Enter a valid email address.")

        name_part = email.split("@")[0]
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._+-")
        if not all(char in allowed_chars for char in name_part):
            raise serializers.ValidationError(
                "Email name part can only contain letters, digits, '.', '_', '+', '-' characters."
            )

        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered.")

        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["repeat_password"]:
            raise serializers.ValidationError("Passwords don't match")
        validate_password_complexity(attrs["password"])
        return attrs

    def validate_password(self, value):
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase character.")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase character.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/\\\"'" for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        if any(ord(char) < 32 for char in value):
            raise serializers.ValidationError("Password must not contain non-printing characters.")
        return value

    def create(self, validated_data):
        validated_data.pop("repeat_password")
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user
