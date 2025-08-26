from django.core import signing
from django.utils import timezone
from datetime import timedelta

def make_link_token(user_id: int, ttl_minutes=15) -> str:
    payload = {
        "uid": user_id,
        "exp": (timezone.now() + timedelta(minutes=ttl_minutes)).timestamp()
    }
    return signing.dumps(payload, salt="tg-link")

def verify_link_token(token: str) -> int:
    data = signing.loads(token, salt="tg-link")
    if timezone.now().timestamp() > data["exp"]:
        raise signing.BadSignature("Token expired")
    return int(data["uid"])