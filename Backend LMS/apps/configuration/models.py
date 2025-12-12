from django.db import models

from apps.users.models import User
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class SchoolSettings(TimeUserStamps):
    """School Configuration"""
    school_name = models.CharField(max_length=200)
    school_code = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='school/', null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    address = models.TextField()
    established_year = models.IntegerField()
    principal_name = models.CharField(max_length=100)
    academic_year_start_month = models.IntegerField(default=4)  # April
    currency = models.CharField(max_length=10, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    
    class Meta:
        db_table = 'school_settings'
        verbose_name_plural = 'School Settings'


class EmailTemplate(TimeUserStamps):
    """Email Templates"""
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    template_type = models.CharField(max_length=50)  # fee_reminder, result_published, etc.
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'email_templates'


class SMSTemplate(TimeUserStamps):
    """SMS Templates"""
    name = models.CharField(max_length=100)
    message = models.CharField(max_length=160)
    template_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sms_templates'


class AuditLog(TimeUserStamps):
    """System Audit Trail"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']