from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse


class LoginView(TemplateView):
    template_name = "users/login.html"


class RegisterView(TemplateView):
    template_name = "users/register.html"


class ProfileView(TemplateView):
    template_name = "users/profile.html"
