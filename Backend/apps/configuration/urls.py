from django.urls import path
from .views import (
    SchoolSettingsView,
    EmailTemplateView,
    SMSTemplateView,
    AuditLogView
)

urlpatterns = [

    path('v1/school/settings/', SchoolSettingsView.as_view(), name='school-settings'),
    path('v1/email/templates/', EmailTemplateView.as_view(), name='email-templates'),
    path('v1/sms/templates/', SMSTemplateView.as_view(), name='sms-templates'),
    path('v1/audit/logs/', AuditLogView.as_view(), name='audit-logs'),
]