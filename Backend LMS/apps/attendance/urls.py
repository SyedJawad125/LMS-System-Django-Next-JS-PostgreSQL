from django.urls import include, path
from .views import (DailyAttendanceView, MonthlyAttendanceReportView,AttendanceConfigurationView, 
                    AttendanceSummaryView)

urlpatterns = [

    # Simple Attendance URLs
    path('v1/attendance/daily/', DailyAttendanceView.as_view()),
    path('v1/attendance/monthly/', MonthlyAttendanceReportView.as_view()),
    path('v1/attendance/config/', AttendanceConfigurationView.as_view()),
    # path('v1/attendance/summary/', AttendanceSummaryView.as_view()),
    # For list (GET all) and create (POST)
    path('v1/attendance/summary/', AttendanceSummaryView.as_view(), name='attendance-summary-list'),
    
    # For retrieve (GET one), update (PATCH), delete (DELETE) by student_id
    path('v1/attendance/summary/<int:student_id>/', AttendanceSummaryView.as_view(), name='attendance-summary-detail'),
]