from django.urls import include, path
from .views import (
    ExamTypeView, 
    ExamView, 
    ExamScheduleView, 
    ExamResultView, 
    GradeSystemView
)

urlpatterns = [
    path('v1/exam/type/', ExamTypeView.as_view()),
    path('v1/exam/', ExamView.as_view()),
    path('v1/exam/schedule/', ExamScheduleView.as_view()),
    path('v1/exam/result/', ExamResultView.as_view()),
    path('v1/grade/system/', GradeSystemView.as_view()),
]