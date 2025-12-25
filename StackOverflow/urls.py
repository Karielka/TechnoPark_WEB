from django.contrib import admin
from django.urls import path, include
from questions.views import HomeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("questions/", include("questions.urls", namespace="questions")),
    path("", include("users.urls", namespace="users")),
    path("centrifugo/", include("centrifuge_client.urls", namespace="centrifuge_client")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)