from django.conf import settings
from django.db import models

class TelegramAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram"
    )
    chat_id = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}:{self.user.username}{self.chat_id}"