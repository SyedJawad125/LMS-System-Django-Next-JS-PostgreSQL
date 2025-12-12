from django.urls import include, path
from .views import (
    ReportCardView,
    StudentBehaviorView
)

urlpatterns = [
    path('v1/report/card/', ReportCardView.as_view()),
    path('v1/student/behavior/', StudentBehaviorView.as_view()),
]