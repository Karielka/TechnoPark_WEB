import time
import jwt
from django.conf import settings


def make_connection_token(user=None) -> str:
    expire = int(time.time()) + int(settings.CENTRIFUGE_TOKEN_EXPIRE)
    sub = ""
    if user is not None and getattr(user, "is_authenticated", False):
        sub = str(user.pk)

    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.CENTRIFUGE_SECRET, algorithm="HS256")
