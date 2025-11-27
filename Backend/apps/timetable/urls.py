from django.urls import include, path
from .views import (TimeSlotView, TimetableView)

urlpatterns = [
    path('v1/timeslot/', TimeSlotView.as_view()),
    path('v1/timetable/', TimetableView.as_view()),
]