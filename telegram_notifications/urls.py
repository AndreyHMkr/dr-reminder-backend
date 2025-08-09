from django.urls import path

from telegram_notifications.views import link_telegram_account

urlpatterns = [
    path("link/", link_telegram_account, name="link-telegram"),
]