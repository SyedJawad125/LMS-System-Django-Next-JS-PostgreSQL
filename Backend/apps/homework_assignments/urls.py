from django.urls import include, path
from .views import (
    AssignmentView,
    AssignmentSubmissionView
)

urlpatterns = [
    path('v1/assignment/', AssignmentView.as_view()),
    path('v1/assignment/submission/', AssignmentSubmissionView.as_view()),
]