# exams/urls.py
from django.urls import path
from .views import StartExamAPI, SubmitExamAPI, PaperStatsAPI, QuestionChoiceStatsAPI

urlpatterns = [
    path('start/', StartExamAPI.as_view()),
    path('submit/', SubmitExamAPI.as_view()),
    path('admin/papers/<int:paper_id>/stats/', PaperStatsAPI.as_view()),
    path('questions/<int:question_id>/choice-stats/', QuestionChoiceStatsAPI.as_view()),
]
