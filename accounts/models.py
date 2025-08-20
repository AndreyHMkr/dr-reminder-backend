import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.template.defaultfilters import slugify
from django.conf import settings


class UserSettings(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        PROVIDERS_ONLY = "providers_only", "Healthcare providers only"

    class Units(models.TextChoices):
        METRIC = "metric", "Metric (kg, °C)"
        IMPERIAL = "imperial", "Imperial (lbs, °F)"

    class DataFormat(models.TextChoices):
        MDY = "MM/DD/YYYY", "MM/DD/YYYY"
        DMY = "DD/MM/YYYY", "DD/MM/YYYY"
        ISO = "YYYY-MM-DD", "YYYY-MM-DD"

    class TimeZones(models.TextChoices):
        AMERICA_NEW_YORK   = "America/New_York",   "Eastern Time"
        AMERICA_CHICAGO    = "America/Chicago",    "Central Time"
        AMERICA_DENVER     = "America/Denver",     "Mountain Time"
        AMERICA_LOS_ANGELES= "America/Los_Angeles","Pacific Time"
        EUROPE_KYIV        = "Europe/Kyiv",        "Eastern European Time"
        EUROPE_DUBLIN      = "Europe/Dublin",      "Ireland (Dublin)"


    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings")
    profile_visibility = models.CharField(max_length=32, choices=Visibility.choices, default=Visibility.PRIVATE)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    appointment_notifications = models.BooleanField(default=True)
    medication_reminders = models.BooleanField(default=True)

    two_factor_enabled = models.BooleanField(default=False)

    timezone = models.CharField(max_length=64, choices=TimeZones.choices, default=TimeZones.EUROPE_KYIV)
    date_format = models.CharField(max_length=16, choices=DataFormat.choices, default=DataFormat.ISO)
    units = models.CharField(max_length=16, choices=Units.choices, default=Units.METRIC)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings({self.user_id})"


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields["is_staff"]:
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields["is_superuser"]:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ('admin', "Admin"),
        ('user', "User"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


class SexChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


def create_custom_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/images/",
        f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
    )


class UserProfile(models.Model):
    image_profile = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, unique=False, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SexChoices, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class HealthIndicators(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pulse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(220)],
        help_text="Heart rate in beats per minute"
    )
    blood_pressure = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(250)],
        help_text="Blood pressure"

    )
    temperature = models.FloatField(
        validators=[MinValueValidator(30), MaxValueValidator(45)],
        help_text="Body temperature in 36.6°C"
    )
    weight = models.FloatField(
        validators=[MinValueValidator(2), MaxValueValidator(500)],
        help_text="Body weight in kilograms 70.5"
    )
    height = models.FloatField(
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="Height in centimeters"
    )

    def __str__(self):
        return f"Health Indicator for {self.user}"


def doc_upload_path(instance, filename):
    # /medical_documents/<user_id>/<filename>
    return f"medical_documents/{instance.user_id}/{filename}"


class MedicalDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=doc_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} ({self.user_id})"
