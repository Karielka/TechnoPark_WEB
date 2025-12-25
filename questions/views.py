from django.views import View
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
from .models import Question, Answer, Tag, QuestionMark, AnswerMark
from .forms import QuestionForm, AnswerForm


class HomeView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_number = int(self.request.GET.get("page", 1))
        questions, total_pages = Question.objects.get_new_question(page_number)
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
        questions, total_pages = Question.objects.get_hot_question(page_number)
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
        questions, total_pages = Question.objects.get_tag_question(tag, page_number)
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
            "answers": answers,
            "answer_form": AnswerForm(),
        })
        return ctx


class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "questions/question_create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        tags = form.cleaned_data.get("tags", [])
        if tags:
            tag_ids = []
            for title in tags:
                t, _ = Tag.objects.get_or_create(title=title)
                tag_ids.append(t.id)
            self.object.tags.set(tag_ids)

        return redirect("questions:question_detail", pk=self.object.pk)


class QuestionUpdateView(TemplateView):
    template_name = "questions/question_update.html"


class QuestionDeleteView(TemplateView):
    template_name = "questions/question_confirm_delete.html"


class AnswerCreateView(View):
    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = request.user
            answer.question = question
            answer.save()
            answer.question.add_answer()
            return redirect("questions:question_detail", pk=question.id)

        answers = Answer.objects.filter(question=question).order_by("created_at")
        return render(request, "questions/question_detail.html", {
            "question": question,
            "answers": answers,
            "answer_form": form,
        })
    

class QuestionMarkAjaxView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "auth_required"}, status=403)

        question = get_object_or_404(Question, pk=pk)

        mark = request.POST.get("mark")

        if mark == "like":
            mark = 1
        elif mark == "dislike":
            mark = -1

        try:
            mark = int(mark)
        except (TypeError, ValueError):
            return JsonResponse({"error": "bad_mark"}, status=400)

        if mark not in (1, -1):
            return JsonResponse({"error": "bad_mark"}, status=400)

        existing = QuestionMark.objects.filter(user=request.user, question=question).first()

        # rating может быть None в БД, на всякий случай
        question.rating = question.rating or 0

        if existing:
            # Если нажал ту же оценку — снимаем
            if existing.mark == mark:
                existing.delete()
                question.rating -= mark
                question.save(update_fields=["rating"])
                return JsonResponse({"rating": question.rating, "mark": 0})

            # Если была противоположная — переключаем
            question.rating += (mark - existing.mark)
            existing.mark = mark
            existing.save(update_fields=["mark"])
            question.save(update_fields=["rating"])
            return JsonResponse({"rating": question.rating, "mark": mark})

        # Если оценки не было — создаём
        QuestionMark.objects.create(user=request.user, question=question, mark=mark)
        question.rating += mark
        question.save(update_fields=["rating"])
        return JsonResponse({"rating": question.rating, "mark": mark})
    

class AnswerMarkAjaxView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "auth_required"}, status=403)

        answer = get_object_or_404(Answer, pk=pk)

        mark = request.POST.get("mark")

        if mark == "like":
            mark = 1
        elif mark == "dislike":
            mark = -1

        try:
            mark = int(mark)
        except (TypeError, ValueError):
            return JsonResponse({"error": "bad_mark"}, status=400)

        if mark not in (1, -1):
            return JsonResponse({"error": "bad_mark"}, status=400)

        existing = AnswerMark.objects.filter(user=request.user, answer=answer).first()

        answer.rating = answer.rating or 0

        # Если уже было — снимаем или переключаем
        if existing:
            if existing.mark == mark:
                existing.delete()
                answer.rating -= mark
                answer.save(update_fields=["rating"])
                return JsonResponse({"rating": answer.rating, "mark": 0, "answer_id": answer.id})

            answer.rating += (mark - existing.mark)
            existing.mark = mark
            existing.save(update_fields=["mark"])
            answer.save(update_fields=["rating"])
            return JsonResponse({"rating": answer.rating, "mark": mark, "answer_id": answer.id})

        # Если не было — создаём
        AnswerMark.objects.create(user=request.user, answer=answer, mark=mark)
        answer.rating += mark
        answer.save(update_fields=["rating"])
        return JsonResponse({"rating": answer.rating, "mark": mark, "answer_id": answer.id})


class AnswerCorrectAjaxView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "auth_required"}, status=403)

        question = get_object_or_404(Question, pk=pk)

        if question.user_id != request.user.id:
            return JsonResponse({"error": "not_allowed"}, status=403)

        answer_id = request.POST.get("answer_id")
        try:
            answer_id = int(answer_id)
        except (TypeError, ValueError):
            return JsonResponse({"error": "bad_answer_id"}, status=400)

        answer = get_object_or_404(Answer, pk=answer_id, question_id=question.id)

        # если уже правильный — снимаем
        if answer.is_correct:
            Answer.objects.filter(question_id=question.id, is_correct=True).update(is_correct=False)
            return JsonResponse({"ok": True, "answer_id": 0})

        # иначе: снимаем прошлый и ставим новый
        Answer.objects.filter(question_id=question.id, is_correct=True).update(is_correct=False)
        Answer.objects.filter(pk=answer.id).update(is_correct=True)

        return JsonResponse({"ok": True, "answer_id": answer.id})