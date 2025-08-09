from django.utils import timezone
from celery import shared_task
from django.db.models import OuterRef, Subquery
from services.models import TreatmentIntake
from telegram_notifications.models import TelegramAccount
from telegram_notifications.notify import send_telegram_message
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_due_treatment_intakes():
    now = timezone.now()
    print(now)

    chat_id_sq = (
        TelegramAccount.objects
        .filter(user=OuterRef('plan__user'), is_active=True)
        .order_by('-linked_at')
        .values('chat_id')[:1]
    )

    qs = (
        TreatmentIntake.objects
        .select_related('plan', 'plan__user')
        .filter(is_active=True, next_run__isnull=False, next_run__lte=now)
        .annotate(chat_id=Subquery(chat_id_sq))
    )

    logger.info("Due intakes count: %s", qs.count())

    for intake in qs:
        logger.info("Intake id=%s user_id=%s chat_id=%s next_run=%s",
                    intake.id, intake.plan.user_id, intake.chat_id, intake.next_run)

        med = intake.plan.name_of_medicine
        when = intake.time.strftime("%H:%M")
        text = f"💊 Reminder: It's time to accept <b>{med}</b> in {when}."

        if intake.chat_id:
            try:
                send_telegram_message(intake.chat_id, text)
                logger.info("Sent to %s", intake.chat_id)
            except Exception:
                logger.exception("Send failed for intake %s", intake.id)
        else:
            logger.warning("Not found chat_id for user_id=%s", intake.plan.user_id)

        intake.schedule_next_run()