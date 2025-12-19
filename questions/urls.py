from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [

    path("ask/",             views.QuestionCreateView.as_view(), name="ask"),
    path("<int:pk>/",        views.QuestionDetailView.as_view(), name="question_detail"),
    path("<int:pk>/edit/",   views.QuestionUpdateView.as_view(), name="question_update"),
    path("<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="question_delete"),

    # создать ответ для вопроса pk
    path("<int:pk>/answer/", views.AnswerCreateView.as_view(), name="answer_create"),

    path("hot/", views.HotView.as_view(), name="hot"),
    path("tag/<str:tag>/", views.TagView.as_view(), name="tag"),
]
