from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from django.db import transaction, IntegrityError
from .utils import make_link_token, verify_link_token

User = get_user_model()
from .models import TelegramAccount

@api_view(["POST"])
@permission_classes([AllowAny])
def link_by_token(request):
    code = request.data.get("token")
    chat_id = request.data.get("chat_id")

    if not code or not chat_id:
        return Response({"detail": "token and chat_id are required"}, status=400)

    # verify_link_token возвращает ИД пользователя
    try:
        user_id = int(verify_link_token(code))
    except Exception:
        return Response({"detail": "invalid_or_expired_token"}, status=400)

    chat_id = str(chat_id)

    try:
        with transaction.atomic():
            obj, created = TelegramAccount.objects.get_or_create(
                chat_id=chat_id,
                defaults={"user_id": user_id}
            )

            if not created and obj.user_id != user_id:
                obj.user_id = user_id
                obj.save(update_fields=["user_id"])

    except IntegrityError:
        obj = TelegramAccount.objects.get(chat_id=chat_id)
        if obj.user_id != user_id:
            return Response(
                {"detail": "chat_already_linked_to_another_user"},
                status=status.HTTP_409_CONFLICT,
            )
    return Response({"linked": True}, status=200)

@api_view(["POST"])
@permission_classes([AllowAny])
def toggle_by_chat(request):
    chat_id = str(request.data.get("chat_id"))
    is_active = request.data.get("is_active")
    if chat_id is None or is_active is None:
        return Response({"detail": "chat_id and is_active required"}, status=400)

    try:
        acc = TelegramAccount.objects.get(chat_id=chat_id)
    except TelegramAccount.DoesNotExist:
        return Response({"detail": "not_found"}, status=404)

    acc.is_active = bool(is_active)
    acc.save(update_fields=["is_active"])
    return Response({"is_active": acc.is_active}, status=200)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    token = make_link_token(request.user.id)
    return Response({"token": token})


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