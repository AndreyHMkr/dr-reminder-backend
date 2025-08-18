from datetime import timedelta

from django.db import models
from django.utils import timezone

from django.conf import settings


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


class TreatmentPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name_of_medicine = models.CharField()
    description = models.TextField()
    start_date = models.DateField()
    finish_date = models.DateField()

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name_of_medicine} ({self.user_id})"


class TreatmentIntake(models.Model):
    plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE, related_name="intakes")
    time = models.TimeField()
    next_run = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def schedule_next_run(self):
        now = timezone.now()
        start = self.plan.start_date
        if start is not None and now.date() < start:
            next_run = start
        else:
            next_run = now.replace(hour=self.time.hour, minute=self.time.minute, second=0, microsecond=0)
            if next_run < now:
                next_run += timedelta(days=1)

        self.next_run = next_run
        self.save()


class MedicalSpecialty(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class EventType(models.TextChoices):
    VACCINATION = "vaccination", "Vaccination"
    ANALYSIS = "analysis", "Analysis"
    BLOOD_DONATION = "blood donation", "Blood Donation"
    OTHER = "other", "Other"
    VISIT = "visit", "Visit"


class Event(models.Model):
    class Meta:
        ordering = ["start_date"]
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    short_description = models.TextField(blank=True)
    start_date = models.DateField()
    start_time = models.TimeField()
    medical_specialty = models.ForeignKey("MedicalSpecialty", null=True, blank=True, on_delete=models.SET_NULL)
    vaccination = models.ForeignKey("Vaccination", null=True, blank=True, on_delete=models.SET_NULL)
    analysis_test = models.ForeignKey("AnalysisTest", null=True, blank=True, on_delete=models.SET_NULL)
    blood_donation = models.OneToOneField("BloodDonation", null=True, blank=True, on_delete=models.CASCADE, related_name="event", db_column="blood_donation_id",
)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.OTHER)
    created_at = models.DateTimeField(auto_now_add=True)

    SERVICE_TYPE_MAP = {
        "mri": EventType.ANALYSIS,
        "dentist": EventType.VISIT,
        "ultrasound": EventType.ANALYSIS,
        "therapy": EventType.VISIT,
    }
    SERVICE_BY_EVENT_TYPE = {
        EventType.VISIT: "visit",
        EventType.VACCINATION: "vaccination",
        EventType.ANALYSIS: "analysis",
        EventType.BLOOD_DONATION: "blood-donation",
        EventType.OTHER: "other",
    }

    def _autofill_service(self):
        if self.service or not self.event_type:
            return
        slug = self.SERVICE_BY_EVENT_TYPE.get(self.event_type)
        if not slug:
            return
        try:
            self.service = Service.objects.get(slug=slug)
        except Service.DoesNotExist:
            pass
    def save(self, *args, **kwargs):
        if self.medical_specialty:
            self.name = f"Visit to {self.medical_specialty.title}"
            self.event_type = EventType.VISIT
        elif self.vaccination:
            self.name = f"Vaccination against {self.vaccination.title}"
            self.event_type = EventType.VACCINATION
        elif self.analysis_test:
            self.name = self.analysis_test.title
            self.event_type = EventType.ANALYSIS
        elif self.blood_donation:
            self.name = "Blood donation"
            self.event_type = EventType.BLOOD_DONATION
        elif self.service:
            self.name = self.service.title
            mapped = self.SERVICE_TYPE_MAP.get(self.service.slug)
            self.event_type = mapped or EventType.OTHER
        else:
            self.name = "Other"
            self.event_type = EventType.OTHER

        self._autofill_service()

        super().save(*args, **kwargs)


class Vaccination(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    vaccine_info = models.TextField()

    def __str__(self):
        return self.title


class AnalysisPackage(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class AnalysisTest(models.Model):
    package = models.ForeignKey(AnalysisPackage, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title
class DonationCenter(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["city", "title"]

    def __str__(self):
        return self.title

class BloodDonation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    center = models.ForeignKey(DonationCenter, on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        ordering = ["-date", "-time"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date", "time"],
                name="uniq_blood_donation_user_date_time",

            )
        ]
    def __str__(self):
        return f"{self.center.title}"
