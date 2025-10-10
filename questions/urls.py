from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [

    path("new/",             views.QuestionCreateView.as_view(), name="create"),
    path("<int:pk>/",        views.QuestionDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/",   views.QuestionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="delete"),

    
]
