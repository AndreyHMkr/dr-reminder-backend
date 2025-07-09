from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from jwt.utils import force_bytes
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


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("There is no user with this email.")
        self.context["user"] = user
        return value

    def save(self, request=None):
        user = self.context.get("user")
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        token = default_token_generator.make_token(user)
        reset_url = f"http://frontend-domain.com/reset-password-confirm/?uid={uid}&token={token}"
        from_email = f"{settings.SITE_NAME} <{settings.DEFAULT_FROM_EMAIL}>"

        send_mail(
            subject="Reset your password",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=from_email,
            recipient_list=[user.email],
        )


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, max_length=30, write_only=True)
    repeat_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["repeat_password"]:
            raise serializers.ValidationError("Password and repeat password must match.")
        validate_password_complexity(attrs["new_password"])
        return attrs

    def save(self):
        try:
            uid = urlsafe_base64_decode(self.validated_data["uid"]).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise serializers.ValidationError("User with this ID does not exist.")

        token = self.validated_data["token"]
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token")
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
