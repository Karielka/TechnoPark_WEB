from django.urls import path
from . import views

app_name = "users"

urlpatterns = [

    path("login/",     views.LoginView.as_view(), name="login"),
    path("profile/",   views.ProfileView.as_view(), name="profile"),
    path("register/",  views.RegisterView.as_view(), name="register"),

]
