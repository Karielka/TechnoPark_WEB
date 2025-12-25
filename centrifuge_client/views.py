from django.http import JsonResponse
from django.views import View
from .tokens import make_connection_token


class CentrifugeTokenView(View):
    def get(self, request):
        token = make_connection_token(request.user)
        return JsonResponse({"token": token})
