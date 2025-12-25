# centrifuge_client/urls.py
from django.urls import path
from .views import CentrifugeTokenView

app_name = "centrifuge_client"

urlpatterns = [
    path("token/", CentrifugeTokenView.as_view(), name="token"),
]
