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



class HomeView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


class QuestionDetailView(TemplateView):
    template_name = "questions/question_detail.html"


class QuestionCreateView(TemplateView):
    template_name = "questions/question_create.html"


class QuestionUpdateView(TemplateView):
    template_name = "questions/question_update.html"


class QuestionDeleteView(TemplateView):
    template_name = "questions/question_confirm_delete.html"
