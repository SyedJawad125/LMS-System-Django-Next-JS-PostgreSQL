from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import models

from utils.reusable_classes import TimeUserStamps


class AttendanceStatus(models.TextChoices):
    """Centralized status choices for maintainability"""
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LATE = 'late', 'Late'
    HALF_DAY = 'half_day', 'Half Day'
    EXCUSED = 'excused', 'Excused'
    HOLIDAY = 'holiday', 'Holiday'
    SICK_LEAVE = 'sick_leave', 'Sick Leave'


class DailyAttendance(TimeUserStamps):
    """Daily Attendance Records - Simplified (validation moved to serializer)"""
    
    student = models.ForeignKey(
        'users.Student',  # ✅ CORRECT - uses 'users' app
        on_delete=models.CASCADE, 
        related_name='daily_attendances',
        db_index=True
    )
    date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20, 
        choices=AttendanceStatus.choices,
        db_index=True
    )
    subject = models.ForeignKey(
        'academic.Subject',  # ✅ CORRECT - uses 'academic' app (singular)
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_index=True
    )
    section = models.ForeignKey(
        'academic.Section',  # ✅ CORRECT - uses 'academic' app (singular)
        on_delete=models.CASCADE,
        db_index=True
    )
    marked_by = models.ForeignKey(
        'users.Teacher',  # ✅ CORRECT - uses 'users' app
        on_delete=models.SET_NULL, 
        null=True,
        related_name='marked_attendances'
    )
    remarks = models.TextField(blank=True)
    
    # For late arrivals
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # For verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'users.Teacher',  # ✅ CORRECT - uses 'users' app
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_attendances'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'daily_attendance'
        indexes = [
            models.Index(fields=['student', 'date', 'subject']),
            models.Index(fields=['section', 'date']),
            models.Index(fields=['date', 'status']),
        ]
        unique_together = ['student', 'date', 'subject']
        ordering = ['-date', 'student']
        verbose_name = 'Daily Attendance'
        verbose_name_plural = 'Daily Attendances'

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"


class MonthlyAttendanceReport(TimeUserStamps):
    """Monthly Attendance Summary - Simplified (calculations moved to serializer)"""
    
    student = models.ForeignKey(
        'users.Student',  # ✅ CORRECT - uses 'users' app
        on_delete=models.CASCADE,
        related_name='monthly_reports',
        db_index=True
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveIntegerField()
    
    # Breakdown by status
    total_school_days = models.PositiveSmallIntegerField(default=0)
    present_days = models.PositiveSmallIntegerField(default=0)
    absent_days = models.PositiveSmallIntegerField(default=0)
    late_days = models.PositiveSmallIntegerField(default=0)
    half_days = models.PositiveSmallIntegerField(default=0)
    excused_days = models.PositiveSmallIntegerField(default=0)
    sick_leave_days = models.PositiveSmallIntegerField(default=0)
    
    # Calculated metrics (set by serializer)
    attendance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    punctuality_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    previous_month_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    percentage_change = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    
    # Metadata
    is_finalized = models.BooleanField(default=False)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'monthly_attendance_reports'
        unique_together = ['student', 'month', 'year']
        indexes = [
            models.Index(fields=['student', 'year', 'month']),
            models.Index(fields=['attendance_percentage']),
            models.Index(fields=['is_finalized']),
        ]
        ordering = ['-year', '-month', 'student']
        verbose_name = 'Monthly Attendance Report'
        verbose_name_plural = 'Monthly Attendance Reports'

    def __str__(self):
        return f"{self.student} - {self.month:02d}/{self.year} - {self.attendance_percentage}%"


class AttendanceConfiguration(TimeUserStamps):
    """Configuration for attendance calculations - Simplified"""
    
    section = models.ForeignKey(
        'academic.Section',  # ✅ CORRECT - uses 'academic' app (singular)
        on_delete=models.CASCADE,
    )
    
    # School timing
    school_start_time = models.TimeField(default='08:00')
    school_end_time = models.TimeField(default='15:00')
    
    # Late arrival threshold
    late_arrival_threshold = models.PositiveSmallIntegerField(
        default=15,
        help_text="Minutes after start time considered as late"
    )
    
    # Minimum attendance requirements
    min_attendance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=75.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Half day configuration
    half_day_threshold = models.PositiveSmallIntegerField(
        default=4,
        help_text="Hours required to count as full day"
    )
    
    # Auto-calculation settings
    auto_generate_reports = models.BooleanField(
        default=True,
        help_text="Automatically generate monthly reports"
    )
    report_generation_day = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text="Day of month to generate reports"
    )

    class Meta:
        db_table = 'attendance_configuration'
        verbose_name = 'Attendance Configuration'
        verbose_name_plural = 'Attendance Configurations'

    def __str__(self):
        return f"Attendance Config - {self.section}"


class AttendanceSummary(TimeUserStamps):
    """Quick lookup table for attendance summaries - Simplified"""
    
    student = models.OneToOneField(
        'users.Student',  # ✅ CORRECT - uses 'users' app
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='attendance_summary'
    )
    
    # Current academic year totals
    current_year = models.PositiveIntegerField()
    total_days = models.PositiveSmallIntegerField(default=0)
    days_present = models.PositiveSmallIntegerField(default=0)
    days_absent = models.PositiveSmallIntegerField(default=0)
    days_late = models.PositiveSmallIntegerField(default=0)
    days_half_day = models.PositiveSmallIntegerField(default=0)
    days_excused = models.PositiveSmallIntegerField(default=0)
    
    # Overall percentage (calculated by serializer)
    overall_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Current streak
    current_streak = models.PositiveSmallIntegerField(
        default=0,
        help_text="Consecutive present days"
    )
    
    # Last updated
    last_calculated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_summary'
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'
        indexes = [
            models.Index(fields=['overall_percentage']),
            models.Index(fields=['current_streak']),
        ]

    def __str__(self):
        return f"{self.student} - {self.overall_percentage}%"