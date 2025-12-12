from django.urls import path
from .views import (
    SchoolSettingsView,
    EmailTemplateView,
    SMSTemplateView,
    AuditLogView
)

urlpatterns = [

    path('v1/school/setting/', SchoolSettingsView.as_view(), name='school-settings'),
    path('v1/email/template/', EmailTemplateView.as_view(), name='email-templates'),
    path('v1/sms/template/', SMSTemplateView.as_view(), name='sms-templates'),
    path('v1/audit/log/', AuditLogView.as_view(), name='audit-logs'),
]