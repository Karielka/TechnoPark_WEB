from urllib.parse import urljoin
from django.conf import settings


def centrifugo_http_base() -> str:
    host = (settings.CENTRIFUGE_HOST or "").rstrip("/") + "/"
    prefix = (getattr(settings, "CENTRIFUGE_URL", "") or "").strip("/")
    if prefix:
        host = urljoin(host, prefix + "/")
    return host.rstrip("/")


def centrifugo_api_url() -> str:
    return urljoin(centrifugo_http_base() + "/", "api")


def centrifugo_ws_url() -> str:
    http = centrifugo_http_base()
    if http.startswith("https://"):
        ws = "wss://" + http[len("https://"):]
    elif http.startswith("http://"):
        ws = "ws://" + http[len("http://"):]
    else:
        ws = http
    return ws.rstrip("/") + "/connection/websocket"
