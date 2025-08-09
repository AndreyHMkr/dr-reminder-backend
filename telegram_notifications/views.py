from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from telegram_notifications.models import TelegramAccount


# class SaveChatIdView(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request, *args, **kwargs):
#         chat_id = request.data.get("chat_id")
#         if not chat_id:
#             return Response({"detail": "chat_id is required"}, status=400)
#         acc, _ = TelegramAccount.objects.update_or_create(
#             user=request.user,
#             defaults={"chat_id": str(chat_id), "is_active": True},
#         )
#         return Response({"chat_id": acc.chat_id}, status=status.HTTP_200_OK)


# telegram_notifications/views.py
# telegram_notifications/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import TelegramAccount

User = get_user_model()

# telegram_notifications/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import TelegramAccount

User = get_user_model()

@api_view(['POST'])
def link_telegram_account(request):
    email = request.data.get('email')
    chat_id = request.data.get('chat_id')

    if not email or not chat_id:
        return Response({'detail': 'Email and chat_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    TelegramAccount.objects.update_or_create(
        user=user,
        defaults={"chat_id": chat_id, "is_active": True}
    )

    return Response({'detail': 'Telegram account linked successfully.'})
