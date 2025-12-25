from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

EXEMPT_URL_NAMES = {
    "users:login",
    "users:logout",
}
EXEMPT_PATH_PREFIXES = (
    "/static/",
    "/media/",
    "/admin/",
    "/admin/login/",
    "/signup/",
)

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if request.user.is_authenticated:
            return self.get_response(request)

        if path.startswith(EXEMPT_PATH_PREFIXES):
            return self.get_response(request)

        try:
            match = resolve(path)
            full_name = (
                f"{match.app_name}:{match.url_name}"
                if match.app_name else match.url_name
            )
        except Exception:
            full_name = None

        if full_name in EXEMPT_URL_NAMES:
            return self.get_response(request)

        return redirect(settings.LOGIN_URL)
