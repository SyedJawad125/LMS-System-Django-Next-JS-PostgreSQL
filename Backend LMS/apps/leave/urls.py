from django.urls import path
from .views import (
    LeaveTypeView,
    LeaveApplicationView,
    LeaveBalanceView,
    LeaveConfigurationView,
    LeaveApprovalWorkflowView,
    LeaveHistoryView
)

urlpatterns = [
    path('v1/leave/type/', LeaveTypeView.as_view()),
    path('v1/leave/application/', LeaveApplicationView.as_view()),
    path('v1/leave/balance/', LeaveBalanceView.as_view()),
    path('v1/leave/configuration/', LeaveConfigurationView.as_view()),
    path('v1/leave/approval/workflow/', LeaveApprovalWorkflowView.as_view()),
    path('v1/leave/history/', LeaveHistoryView.as_view()),
]