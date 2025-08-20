import os

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework import serializers

from accounts.models import UserProfile, HealthIndicators, MedicalDocument, UserSettings
from django.conf import settings
from services.utils.recommendations import generate_recommendations


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
        fields = ("id", "email", "password", "repeat_password", "is_staff",)
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
        password = attrs.get("password")
        repeat = attrs.get("repeat_password")
        if password is not None or repeat is not None:
            if password != repeat:
                raise serializers.ValidationError("Passwords don't match")
            validate_password_complexity(password)
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeat_password")
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("repeat_password", None)
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    image_profile = serializers.ImageField(required=False, allow_null=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "user",
            "username",
            "phone_number",
            "email",
            "birth_date",
            "sex",
            "country",
            "city",
            "image_profile"
        )



class MedicalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDocument
        fields = (
            "id",
            "title",
            "file",
            "uploaded_at",
        )

    def validate(self, attrs):
        file = attrs.get("file")
        title = attrs.get("title")
        if not title and file:
            attrs["title"] = os.path.splitext(file.name)[0]

        user = self.context["request"].user
        t = attrs.get("title")
        if t and MedicalDocument.objects.filter(user=user, title=t).exists():
            raise serializers.ValidationError({"title": "Document with this title already exists."})

        return attrs

class MedicalDocumentBulkUploadSerializer(serializers.Serializer):
    file = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )

    def create(self, validated_data):
        user = self.context["request"].user
        docs = []
        for file in validated_data["file"]:
            title = os.path.splitext(file.name)[0]
            base, idx = title, 1
            while MedicalDocument.objects.filter(user=user, title=title).exists():
                title = f"{base} ({idx})"
                idx += 1
            docs.append(MedicalDocument.objects.create(user=user, title=title, file=file))
        return docs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_user_model().objects.filter(email__iexact=value).first()
        self.context["user"] = user
        return value

    def save(self, request=None):
        user = self.context.get("user")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
        CONFIRM_PATH = "/reset-password-confirm/"
        base = FRONTEND_URL.rstrip("/")
        path = CONFIRM_PATH if CONFIRM_PATH.startswith("/") else f"/{CONFIRM_PATH}"
        reset_url = f"{base}{path}?uid={uid}&token={token}"

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


class HealthIndicatorsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recommendations = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = HealthIndicators
        fields = (
            "id",
            "user",
            "pulse",
            "blood_pressure",
            "temperature",
            "weight",
            "height",
            "recommendations"
        )

    def get_recommendations(self, obj):
        data = {
            "pulse": obj.pulse,
            "blood_pressure": obj.blood_pressure,
            "temperature": obj.temperature,
            "weight": obj.weight,
            "height": obj.height,
        }
        return generate_recommendations(data)


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = (
            "profile_visibility",
            "email_notifications", "push_notifications",
            "sms_notifications", "appointment_notifications",
            "medication_reminders", "timezone", "date_format",
            "units", "two_factor_enabled",
        )
        read_only_fields = ("two_factor_enabled",)

    def validate_timezone(self, value):
        if not value or len(value) > 64:
            raise serializers.ValidationError("Invalid timezone.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, max_length=30, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": "Wrong password."})
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords must match."})
        validate_password_complexity(attrs["new_password"])
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError({"password": "Wrong password."})
        return attrs