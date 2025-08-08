from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from telegram_notifications.models import TelegramAccount


class SaveChatIdView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        chat_id = request.data.get("chat_id")
        if not chat_id:
            return Response({"detail": "chat_id is required"}, status=400)
        acc, _ = TelegramAccount.objects.update_or_create(
            user=request.user,
            defaults={"chat_id": str(chat_id), "is_active": True},
        )
        return Response({"chat_id": acc.chat_id}, status=status.HTTP_200_OK)