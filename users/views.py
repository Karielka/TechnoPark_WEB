from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import CreateView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .forms import LoginForm, SignupForm, ProfileUpdateForm
from .models import UserProfile
from questions.views import SidebarCacheMixin

class LoginView(SidebarCacheMixin, DjangoLoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("users:login")
    http_method_names = ["post",]


class SignupView(SidebarCacheMixin, FormView):
    template_name = "users/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())


class ProfileView(SidebarCacheMixin, TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        ctx.update({"profile": profile})
        return ctx


class ProfileEditView(SidebarCacheMixin, FormView):
    template_name = "users/profile_edit.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("users:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        kwargs["instance"] = profile
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())