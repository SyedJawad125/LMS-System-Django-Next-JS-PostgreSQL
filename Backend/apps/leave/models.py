from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from utils.enums import *
from utils.reusable_classes import TimeUserStamps
import uuid


class LeaveType(TimeUserStamps):
    """Types of Leave with auto-generated code"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, editable=False)
    max_days_per_year = models.IntegerField(default=30)
    requires_approval = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'leave_types'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)
    
    def _generate_code(self):
        """Generate unique code from name (check all records including deleted)"""
        base_code = self.name.upper().replace(' ', '_')[:15]
        counter = 1
        code = base_code
        
        while LeaveType.objects.filter(code=code).exists():
            code = f"{base_code}_{counter}"
            counter += 1
        
        return code
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LeaveApplication(TimeUserStamps):
    """Leave Applications with separate teacher/student fields"""
    
    STATUS_CHOICES = [
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (REJECTED, REJECTED),
        (CANCELLED, CANCELLED)
    ]
    
    application_number = models.CharField(max_length=50, unique=True, editable=False, db_index=True)
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE, null=True, blank=True, related_name='teacher_leave_applications')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='student_leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='applications')
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField(editable=False)
    reason = models.TextField()
    attachment = models.FileField(upload_to='leave_applications/%Y/%m/%d/', null=True, blank=True, max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leave_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    address_during_leave = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leave_applications'
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def clean(self):
        """Validation before saving"""
        if not self.teacher and not self.student:
            raise ValidationError("Either teacher or student must be selected")
        if self.teacher and self.student:
            raise ValidationError("Cannot select both teacher and student")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date")
        if self.start_date and self.start_date < timezone.now().date():
            raise ValidationError("Cannot apply for leave in the past")
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = self._generate_application_number()
        
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
        
        if self.pk:
            try:
                old_instance = LeaveApplication.objects.get(pk=self.pk)
                if old_instance.status == PENDING and self.status != PENDING:
                    if not self.reviewed_at:
                        self.reviewed_at = timezone.now()
            except LeaveApplication.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def _generate_application_number(self):
        """Generate unique application number (check all records including deleted)"""
        prefix = "LV"
        year = timezone.now().strftime('%Y')
        month = timezone.now().strftime('%m')
        
        count = LeaveApplication.objects.filter(
            application_number__startswith=f"{prefix}-{year}{month}"
        ).count() + 1
        
        return f"{prefix}-{year}{month}-{count:04d}"
    
    @property
    def applicant(self):
        """Return the applicant (teacher or student)"""
        return self.teacher or self.student
    
    @property
    def applicant_type(self):
        """Return applicant type"""
        if self.teacher:
            return 'teacher'
        elif self.student:
            return 'student'
        return None
    
    @property
    def applicant_name(self):
        """Return applicant name"""
        if self.teacher:
            if hasattr(self.teacher, 'user') and self.teacher.user:
                full_name = self.teacher.user.get_full_name()
                return full_name.strip() if full_name and full_name.strip() else self.teacher.user.username
            return str(self.teacher)
        elif self.student:
            if hasattr(self.student, 'user') and self.student.user:
                full_name = self.student.user.get_full_name()
                return full_name.strip() if full_name and full_name.strip() else self.student.user.username
            return str(self.student)
        return "Unknown"
    
    @property
    def is_pending(self):
        return self.status == PENDING
    
    @property
    def is_approved(self):
        return self.status == APPROVED
    
    @property
    def can_be_cancelled(self):
        return self.status in [PENDING, APPROVED]
    
    def __str__(self):
        return f"{self.application_number} - {self.applicant_name} - {self.leave_type.name}"


class LeaveBalance(TimeUserStamps):
    """Track leave balances for teachers/students per year"""
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE, null=True, blank=True, related_name='leave_balances')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances')
    academic_year = models.IntegerField()
    total_allocated = models.IntegerField(default=0)
    used = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0, editable=False)
    carried_over = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = [
            ['teacher', 'leave_type', 'academic_year'],
            ['student', 'leave_type', 'academic_year']
        ]
        verbose_name_plural = "Leave Balances"
    
    def clean(self):
        """Validation before saving"""
        if not self.teacher and not self.student:
            raise ValidationError("Either teacher or student must be selected")
        if self.teacher and self.student:
            raise ValidationError("Cannot select both teacher and student")
    
    def save(self, *args, **kwargs):
        self.remaining = (self.total_allocated + self.carried_over) - self.used
        
        if self.remaining < 0:
            raise ValidationError("Remaining days cannot be negative")
        
        super().save(*args, **kwargs)
    
    def allocate_days(self, days):
        """Allocate additional days"""
        self.total_allocated += days
        self.save()
    
    def use_days(self, days):
        """Use leave days"""
        if days > self.remaining:
            raise ValidationError(f"Insufficient balance. Available: {self.remaining}")
        self.used += days
        self.save()
    
    def reset_used_days(self):
        """Reset used days (for new academic year)"""
        self.used = 0
        self.save()
    
    @property
    def applicant(self):
        """Return the applicant (teacher or student)"""
        return self.teacher or self.student
    
    @property
    def applicant_name(self):
        """Return applicant name"""
        if self.applicant:
            if hasattr(self.applicant, 'user') and self.applicant.user:
                full_name = self.applicant.user.get_full_name()
                return full_name.strip() if full_name and full_name.strip() else self.applicant.user.username
            return str(self.applicant)
        return "Unknown"
    
    def __str__(self):
        return f"{self.applicant_name} - {self.leave_type.name} - {self.academic_year}"


class LeaveConfiguration(TimeUserStamps):
    """System-wide leave configuration and rules"""
    academic_year = models.IntegerField(unique=True)
    max_consecutive_days = models.IntegerField(default=30, help_text="Maximum consecutive leave days allowed")
    advance_notice_days = models.IntegerField(default=7, help_text="Minimum advance notice required for leave application")
    max_advance_days = models.IntegerField(default=90, help_text="Maximum days in advance leave can be applied")
    require_multilevel_approval = models.BooleanField(default=False)
    auto_approve_short_leaves = models.BooleanField(default=False, help_text="Auto-approve leaves shorter than specified days")
    auto_approve_max_days = models.IntegerField(default=2, help_text="Maximum days for auto-approval")
    allow_carry_over = models.BooleanField(default=True)
    max_carry_over_days = models.IntegerField(default=10)
    carry_over_validity_months = models.IntegerField(default=3, help_text="Months into next academic year when carried over leaves expire")
    notify_applicant_on_status_change = models.BooleanField(default=True)
    notify_reviewer_on_new_application = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, help_text="Only one configuration can be active at a time")
    
    class Meta:
        db_table = 'leave_configurations'
        verbose_name_plural = "Leave Configurations"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            LeaveConfiguration.objects.filter(deleted=False).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_configuration(cls):
        """Get the currently active configuration (excluding soft deleted)"""
        try:
            return cls.objects.get(is_active=True, deleted=False)
        except cls.DoesNotExist:
            return None
    
    def __str__(self):
        return f"Leave Configuration - Academic Year {self.academic_year}"


class LeaveApprovalWorkflow(TimeUserStamps):
    """Multi-level approval workflow for leaves"""
    LEVEL_CHOICES = [
        (1, 'Level 1 - Immediate Supervisor'),
        (2, 'Level 2 - Department Head'),
        (3, 'Level 3 - HR/Administration'),
        (4, 'Level 4 - Principal/Director')
    ]
    
    leave_application = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE, related_name='approval_workflow')
    approval_level = models.IntegerField(choices=LEVEL_CHOICES)
    approver = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_approvals')
    status = models.CharField(max_length=20, choices=LeaveApplication.STATUS_CHOICES, default=PENDING)
    comments = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True, help_text="Deadline for approval at this level")
    is_current_level = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'leave_approval_workflows'
        ordering = ['approval_level']
        unique_together = ['leave_application', 'approval_level']
    
    def clean(self):
        """Validation before saving"""
        if self.approval_level not in [1, 2, 3, 4]:
            raise ValidationError("Approval level must be between 1 and 4")
    
    def save(self, *args, **kwargs):
        if not self.deadline and not self.pk:
            from datetime import timedelta
            self.deadline = timezone.now() + timedelta(days=3)
        
        if self.status in [APPROVED, REJECTED] and not self.approved_at:
            self.approved_at = timezone.now()
        
        if self.status in [APPROVED, REJECTED] and self.pk:
            LeaveApprovalWorkflow.objects.filter(
                leave_application=self.leave_application,
                deleted=False
            ).exclude(pk=self.pk).update(is_current_level=False)
        
        super().save(*args, **kwargs)
    
    @property
    def approver_name(self):
        """Return approver name"""
        if self.approver:
            if hasattr(self.approver, 'user') and self.approver.user:
                full_name = self.approver.user.get_full_name()
                return full_name.strip() if full_name and full_name.strip() else self.approver.user.username
            return str(self.approver)
        return "Not Assigned"
    
    @property
    def level_name(self):
        """Return approval level name"""
        return dict(self.LEVEL_CHOICES).get(self.approval_level, f"Level {self.approval_level}")
    
    @property
    def is_overdue(self):
        """Check if approval is overdue"""
        if self.deadline and self.status == PENDING:
            return timezone.now() > self.deadline
        return False
    
    def __str__(self):
        return f"{self.leave_application.application_number} - Level {self.approval_level}"


class LeaveHistory(TimeUserStamps):
    """Audit trail for leave applications"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('modified', 'Modified'),
        ('forwarded', 'Forwarded'),
        ('withdrawn', 'Withdrawn')
    ]
    
    leave_application = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    previous_status = models.CharField(max_length=20, choices=LeaveApplication.STATUS_CHOICES, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=LeaveApplication.STATUS_CHOICES, null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True, help_text="JSON representation of changed fields")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leave_history'
        ordering = ['-created_at']
        verbose_name_plural = "Leave Histories"
    
    @property
    def changed_by_name(self):
        """Return name of user who made the change"""
        if self.changed_by:
            full_name = self.changed_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else self.changed_by.username
        return "System"
    
    @property
    def action_display(self):
        """Return human-readable action"""
        return dict(self.ACTION_CHOICES).get(self.action, self.action.title())
    
    def __str__(self):
        return f"{self.leave_application.application_number} - {self.action} at {self.created_at}"