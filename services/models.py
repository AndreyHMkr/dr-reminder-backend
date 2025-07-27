from django.db import models

from dr_reminder_api import settings


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


class MedicalSpecialty(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    medical_specialty = models.ForeignKey("MedicalSpecialty", null=True, blank=True, on_delete=models.SET_NULL)
    vaccination = models.ForeignKey("Vaccination", null=True, blank=True, on_delete=models.SET_NULL)
    analysis_test = models.ForeignKey("AnalysisTest", null=True, blank=True, on_delete=models.SET_NULL)
    blood_donation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.medical_specialty:
            self.name = f"Visit to {self.medical_specialty.title}"
        elif self.vaccination:
            self.name = f"Vaccination against {self.vaccination.title}"
        elif self.analysis_test:
            self.name = self.analysis_test.title
        elif self.blood_donation:
            self.name = "Blood donation"
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

class AnalysisTest(models.Model):
    package = models.ForeignKey(AnalysisPackage, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()