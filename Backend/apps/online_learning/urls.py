from django.urls import include, path
from .views import (
    QuizView, 
    QuestionView, 
    QuizAttemptView, 
    QuizAnswerView,
    QuestionOptionView,
    CourseView,
    LessonView,
    CourseEnrollmentView,
    LessonProgressView
)

urlpatterns = [
    # Quiz/Exam URLs (matching your models)
    path('v1/quiz/', QuizView.as_view()),
    path('v1/question/', QuestionView.as_view()),
    path('v1/question/option/', QuestionOptionView.as_view()),
    path('v1/quiz/attempt/', QuizAttemptView.as_view()),
    path('v1/quiz/answer/', QuizAnswerView.as_view()),
    
    # Course URLs
    path('v1/course/', CourseView.as_view()),
    path('v1/lesson/', LessonView.as_view()),
    path('v1/enrollment/', CourseEnrollmentView.as_view()),
    path('v1/lesson/progress/', LessonProgressView.as_view()),
]