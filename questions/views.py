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

from .temp_db import make_fish_questions, paginate

class HomeView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        questions = make_fish_questions(100)
        page_obj = paginate(questions, self.request, per_page=10)
        ctx.update({
            "page_obj": page_obj,
            "questions": page_obj.object_list,
            "page_title": "Новые вопросы",
        })
        return ctx


class HotView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        questions = sorted(make_fish_questions(57), key=lambda q: q["rating"], reverse=True)
        page_obj = paginate(questions, self.request, per_page=10)
        ctx.update({
            "page_obj": page_obj,
            "questions": page_obj.object_list,
            "page_title": "Горячие вопросы",
        })
        return ctx


class TagView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tag = (kwargs.get("tag") or "").lower()
        all_q = make_fish_questions(57)

        known_tags = {t.lower() for q in all_q for t in q["tags"]}
        if tag not in known_tags:
            render("404.html", {"message": "Тэг не найден"}, status=404)
            return

        filtered = [q for q in all_q if any(t.lower() == tag for t in q["tags"])]
        page_obj = paginate(filtered, self.request, per_page=10)
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
        pk = kwargs.get("pk")
        questions = make_fish_questions(57)
        question = next((q for q in questions if q["id"] == pk), None)
        if not question:
            render("404.html", {"message": "Вопрос не найден"}, status=404)
            return
        answers = [
            {"author": f"User {i}", "text": f"Текст ответа {i} на вопрос {pk}.", "correct": True, "author_avatar_url": "/static/img/avatar.png", "rating": i % 6,}
            for i in range(1, (question["answers_count"] or 1) + 1)
        ]
        ctx.update({"question": question, "answers": answers})
        return ctx


class QuestionCreateView(TemplateView):
    template_name = "questions/question_create.html"


class QuestionUpdateView(TemplateView):
    template_name = "questions/question_update.html"


class QuestionDeleteView(TemplateView):
    template_name = "questions/question_confirm_delete.html"
