from django.conf import settings
from django.db import models


class Service(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title


class Speciality(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="specialities")
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Speciality"
        verbose_name_plural = "Specialities"

    def __str__(self):
        return self.name

class Event(models.Model):
    class EventType(models.TextChoices):
        VISIT = "visit", "Visit"
        VACCINATION = "vaccination", "Vaccination"
        ANALYSIS = "analysis", "Analysis"
        BLOOD_DONATION = "blood donation", "Blood donation"
        MEDICATION = "medication", "Medication"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=EventType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)