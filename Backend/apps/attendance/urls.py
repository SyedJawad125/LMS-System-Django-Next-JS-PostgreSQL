from django.urls import include, path
from .views import (DailyAttendanceView, MonthlyAttendanceReportView,AttendanceConfigurationView, 
                    AttendanceSummaryView)

urlpatterns = [

    # Simple Attendance URLs
    path('v1/attendance/daily/', DailyAttendanceView.as_view()),
    path('v1/attendance/monthly/', MonthlyAttendanceReportView.as_view()),
    path('v1/attendance/config/', AttendanceConfigurationView.as_view()),
    path('v1/attendance/summary/', AttendanceSummaryView.as_view()),
]