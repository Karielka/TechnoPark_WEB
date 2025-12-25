from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Exists, OuterRef

from .models import Question, Answer, Tag, QuestionMark, AnswerMark


def admin_obj_link(obj, label=None):
    """
    Универсальная ссылка на объект в админке Django.
    Работает и с кастомным AUTH_USER_MODEL.
    """
    if not obj:
        return "-"
    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
    return format_html('<a href="{}">{}</a>', url, label or str(obj))


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "topic",
        "user_link",
        "answer_count",
        "rating",
        "has_correct_answer",
        "created_at",
    )
    list_select_related = ("user",)
    search_fields = ("topic", "text", "user__username", "user__email")
    list_filter = ("created_at", "tags")
    autocomplete_fields = ("user", "tags")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        correct_exists = Answer.objects.filter(
            question_id=OuterRef("pk"),
            is_correct=True,
        )
        return qs.annotate(_has_correct_answer=Exists(correct_exists))

    @admin.display(description="Автор")
    def user_link(self, obj: Question):
        return admin_obj_link(obj.user)

    @admin.display(boolean=True, description="Есть правильный ответ")
    def has_correct_answer(self, obj: Question):
        return getattr(obj, "_has_correct_answer", obj.question_answers.filter(is_correct=True).exists())


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "user_link",
        "is_correct",
        "rating",
        "created_at",
    )
    list_select_related = ("user", "question")
    search_fields = ("text", "user__username", "user__email", "question__topic")
    list_filter = ("is_correct", "created_at")
    autocomplete_fields = ("user", "question")
    ordering = ("-created_at",)

    @admin.display(description="Автор")
    def user_link(self, obj: Answer):
        return admin_obj_link(obj.user)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")


@admin.register(QuestionMark)
class QuestionMarkAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "user", "mark")
    list_select_related = ("question", "user")


@admin.register(AnswerMark)
class AnswerMarkAdmin(admin.ModelAdmin):
    list_display = ("id", "answer", "user", "mark")
    list_select_related = ("answer", "user")
