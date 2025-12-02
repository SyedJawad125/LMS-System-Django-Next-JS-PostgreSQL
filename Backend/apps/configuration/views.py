from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    SchoolSettingsSerializer,
    EmailTemplateSerializer,
    SMSTemplateSerializer,
    AuditLogSerializer
)
from .filters import (
    SchoolSettingsFilter,
    EmailTemplateFilter,
    SMSTemplateFilter,
    AuditLogFilter
)


class SchoolSettingsView(BaseView):
    """
    API View for managing school configuration settings
    Handles school profile, contact info, and system preferences
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SchoolSettingsSerializer
    filterset_class = SchoolSettingsFilter
    
    @permission_required([CREATE_SCHOOL_SETTINGS])
    def post(self, request):
        """Create school settings"""
        return super().post_(request)
    
    @permission_required([READ_SCHOOL_SETTINGS])
    def get(self, request):
        """Retrieve school settings"""
        return super().get_(request)
    
    @permission_required([UPDATE_SCHOOL_SETTINGS])
    def patch(self, request):
        """Update school settings"""
        return super().patch_(request)
    
    @permission_required([DELETE_SCHOOL_SETTINGS])
    def delete(self, request):
        """Delete school settings"""
        return super().delete_(request)


class EmailTemplateView(BaseView):
    """
    API View for managing email templates
    Supports dynamic email templates for various notification types
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = EmailTemplateSerializer
    filterset_class = EmailTemplateFilter
    
    @permission_required([CREATE_EMAIL_TEMPLATE])
    def post(self, request):
        """Create a new email template"""
        return super().post_(request)
    
    @permission_required([READ_EMAIL_TEMPLATE])
    def get(self, request):
        """Retrieve email template(s)"""
        return super().get_(request)
    
    @permission_required([UPDATE_EMAIL_TEMPLATE])
    def patch(self, request):
        """Update an existing email template"""
        return super().patch_(request)
    
    @permission_required([DELETE_EMAIL_TEMPLATE])
    def delete(self, request):
        """Delete an email template"""
        return super().delete_(request)


class SMSTemplateView(BaseView):
    """
    API View for managing SMS templates
    Supports 160-character SMS templates for various notification types
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SMSTemplateSerializer
    filterset_class = SMSTemplateFilter
    
    @permission_required([CREATE_SMS_TEMPLATE])
    def post(self, request):
        """Create a new SMS template"""
        return super().post_(request)
    
    @permission_required([READ_SMS_TEMPLATE])
    def get(self, request):
        """Retrieve SMS template(s)"""
        return super().get_(request)
    
    @permission_required([UPDATE_SMS_TEMPLATE])
    def patch(self, request):
        """Update an existing SMS template"""
        return super().patch_(request)
    
    @permission_required([DELETE_SMS_TEMPLATE])
    def delete(self, request):
        """Delete an SMS template"""
        return super().delete_(request)


class AuditLogView(BaseView):
    """
    API View for managing system audit logs
    Tracks all system changes for compliance and security monitoring
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AuditLogSerializer
    filterset_class = AuditLogFilter
    
    @permission_required([CREATE_AUDIT_LOG])
    def post(self, request):
        """Create a new audit log entry"""
        return super().post_(request)
    
    @permission_required([READ_AUDIT_LOG])
    def get(self, request):
        """Retrieve audit log(s)"""
        return super().get_(request)
    
    @permission_required([UPDATE_AUDIT_LOG])
    def patch(self, request):
        """Update an audit log entry"""
        return super().patch_(request)
    
    @permission_required([DELETE_AUDIT_LOG])
    def delete(self, request):
        """Delete an audit log entry"""
        return super().delete_(request)