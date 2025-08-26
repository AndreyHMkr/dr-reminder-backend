from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import signing

from .models import TelegramAccount
from .utils import make_link_token, verify_link_token

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    token = make_link_token(request.user.id)
    return Response({"token": token})


@api_view(["POST"])
def link_by_token(request):
    token = request.data.get("token")
    chat_id = request.data.get("chat_id")

    if not token or not chat_id:
        return Response({"detail": "token и chat_id обязательны"}, status=400)

    try:
        user_id = verify_link_token(token)
    except signing.BadSignature:
        return Response({"detail": "Неверный или просроченный токен"}, status=400)

    user = User.objects.get(id=user_id)
    TelegramAccount.objects.update_or_create(
        user=user,
        defaults={"chat_id": chat_id, "is_active": True}
    )
    return Response({"detail": "Telegram успешно привязан"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_status(request):
    acc = getattr(request.user, "telegram", None)
    if not acc:
        return Response({"linked": False})
    return Response({
        "linked": True,
        "chat_id": acc.chat_id,
        "is_active": acc.is_active,
        "linked_at": acc.linked_at
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def toggle_active(request):
    acc = getattr(request.user, "telegram", None)
    if not acc:
        return Response({"detail": "Не привязан"}, status=404)
    acc.is_active = bool(request.data.get("is_active"))
    acc.save(update_fields=["is_active"])
    return Response({"is_active": acc.is_active})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unlink(request):
    acc = getattr(request.user, "telegram", None)
    if acc:
        acc.delete()
    return Response(status=204)