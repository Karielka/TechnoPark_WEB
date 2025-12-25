import re
import time
import logging

import jwt
from cent import Client, PublishRequest

from django.conf import settings
from .utils import centrifugo_api_url

logger = logging.getLogger(getattr(settings, "PROJECT_NAME", __name__))


def connect_to_centrifuge():
    if not getattr(settings, "CENTRIFUGE_ENABLED", False):
        return None

    url = centrifugo_api_url()
    api_key = settings.CENTRIFUGE_API_KEY
    timeout = settings.CENTRIFUGE_TIMEOUT
    return Client(url, api_key, timeout=timeout)


class BaseChannel(object):
    channel = None
    permissions = []

    SECRET = settings.CENTRIFUGE_SECRET
    EXPIRE = settings.CENTRIFUGE_TOKEN_EXPIRE

    # если пользуешься get_channel_instance, тогда у наследника должен быть channel_pattern
    channel_pattern = r".*"

    def __init__(self, channel=None, centrifuge=None, channel_match=None):
        self.channel = channel
        self.centrifuge = centrifuge
        self.channel_match = channel_match

    def get_channel(self, *args, **kwargs):
        return self.channel

    # ВНИМАНИЕ: это subscription token (если вдруг понадобится),
    # но в текущем решении мы используем connection token из tokens.py
    def get_token(self, channel, user):
        expire = int(time.time()) + self.EXPIRE
        return jwt.encode(
            {"sub": str(user.pk) if user else "", "channel": channel, "exp": expire},
            self.SECRET,
            algorithm="HS256",
        )

    def get_centrifuge(self):
        if self.centrifuge is None:
            self.centrifuge = connect_to_centrifuge()
        return self.centrifuge

    def publish(self, channel, data, msg_type="undefined"):
        client = self.get_centrifuge()
        if client is None:
            return False

        try:
            req = PublishRequest(channel=channel, data={"type": msg_type, "payload": data})
            resp = client.publish(req)
            # resp.error может быть None; при ошибках cent бросает исключения или возвращает ошибку
            if getattr(resp, "error", None):
                logger.error("Centrifugo publish error: %s", resp.error)
                return False
            return True
        except Exception:
            logger.exception("Failed to publish to Centrifugo channel=%s", channel)
            return False

    @classmethod
    def get_channel_instance(cls, channel=None, centrifuge=None):
        match = re.match(cls.channel_pattern, channel or "")
        if match:
            return cls(channel, centrifuge, match)
        return None


class QuestionChannel(BaseChannel):
    """
    Канал: question:<id> (namespace question)
    """
    channel_pattern = r"^question:(?P<question_id>\d+)$"

    @classmethod
    def make(cls, question_id: int) -> str:
        return f"question:{question_id}"
