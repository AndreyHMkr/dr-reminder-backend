from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import TreatmentIntake

@receiver(post_save, sender=TreatmentIntake)
def init_next_run(sender, instance, created, **kwargs):
    if created and instance.is_active and not instance.next_run:
        instance.schedule_next_run()