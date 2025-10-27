from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import TemplateView
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .pagination import paginate
from .utils import QuestionManager
from .models import Question

question_manager = QuestionManager()

class HomeView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_number = int(self.request.GET.get("page", 1))
        questions, total_pages = question_manager.get_new_question(page_number)
        page_obj = paginate(questions, page_number, total_pages)

        ctx.update({
            "page_obj": page_obj,
            "questions": questions,
            "page_title": "Новые вопросы",
        })
        return ctx


class HotView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_number = int(self.request.GET.get("page", 1))
        questions, total_pages = question_manager.get_hot_question(page_number)
        page_obj = paginate(questions, page_number, total_pages)

        ctx.update({
            "page_obj": page_obj,
            "questions": questions,
            "page_title": "Горячие вопросы",
        })
        return ctx


class TagView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tag = kwargs.get("tag")
        page_number = int(self.request.GET.get("page", 1))
        questions, total_pages = question_manager.get_tag_question(tag, page_number)
        page_obj = paginate(questions, page_number, total_pages)

        ctx.update({
            "page_obj": page_obj,
            "questions": page_obj.object_list,
            "current_tag": tag,
            "page_title": f"Вопросы по тегу: {tag}",
        })
        return ctx


class QuestionDetailView(TemplateView):
    template_name = "questions/question_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        question = get_object_or_404(Question, pk=kwargs.get("pk"))
        answers = question.question_answers.all()
        
        ctx.update({
            "question": question, 
            "answers": answers
        })
        return ctx


class QuestionCreateView(TemplateView):
    template_name = "questions/question_create.html"


class QuestionUpdateView(TemplateView):
    template_name = "questions/question_update.html"


class QuestionDeleteView(TemplateView):
    template_name = "questions/question_confirm_delete.html"
