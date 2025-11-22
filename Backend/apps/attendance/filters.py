import django_filters as filters
from django.db.models import Q
from .models import (
    DailyAttendance, MonthlyAttendanceReport, 
    AttendanceConfiguration, AttendanceSummary, AttendanceStatus
)


class DailyAttendanceFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    
    # Foreign key filters
    student = filters.NumberFilter(field_name='student__id')
    section = filters.NumberFilter(field_name='section__id')
    subject = filters.NumberFilter(field_name='subject__id')
    marked_by = filters.NumberFilter(field_name='marked_by__id')
    verified_by = filters.NumberFilter(field_name='verified_by__id')
    
    # Date filters
    date = filters.DateFilter(field_name='date')
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Status filter
    status = filters.ChoiceFilter(choices=AttendanceStatus.choices)
    
    # Boolean filters
    is_verified = filters.BooleanFilter(field_name='is_verified')
    
    class Meta:
        model = DailyAttendance
        fields = [
            'student', 'section', 'subject', 'marked_by', 'verified_by',
            'date', 'date_from', 'date_to', 'status', 'is_verified'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(section__name__icontains=value) |
            Q(subject__name__icontains=value) |
            Q(remarks__icontains=value)
        )


class MonthlyAttendanceReportFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    
    # Foreign key filter
    student = filters.NumberFilter(field_name='student__id')
    
    # Period filters
    month = filters.NumberFilter(field_name='month')
    year = filters.NumberFilter(field_name='year')
    
    # Boolean filter
    is_finalized = filters.BooleanFilter(field_name='is_finalized')
    
    # Percentage range filters
    attendance_percentage_min = filters.NumberFilter(
        field_name='attendance_percentage', 
        lookup_expr='gte'
    )
    attendance_percentage_max = filters.NumberFilter(
        field_name='attendance_percentage', 
        lookup_expr='lte'
    )
    punctuality_score_min = filters.NumberFilter(
        field_name='punctuality_score', 
        lookup_expr='gte'
    )
    punctuality_score_max = filters.NumberFilter(
        field_name='punctuality_score', 
        lookup_expr='lte'
    )
    
    class Meta:
        model = MonthlyAttendanceReport
        fields = [
            'student', 'month', 'year', 'is_finalized',
            'attendance_percentage_min', 'attendance_percentage_max',
            'punctuality_score_min', 'punctuality_score_max'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value)
        )


class AttendanceConfigurationFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    
    # Foreign key filter
    section = filters.NumberFilter(field_name='section__id')
    
    # Boolean filter
    auto_generate_reports = filters.BooleanFilter(field_name='auto_generate_reports')
    
    # Percentage filters
    min_attendance_percentage = filters.NumberFilter(field_name='min_attendance_percentage')
    min_attendance_percentage_gte = filters.NumberFilter(
        field_name='min_attendance_percentage',
        lookup_expr='gte'
    )
    min_attendance_percentage_lte = filters.NumberFilter(
        field_name='min_attendance_percentage',
        lookup_expr='lte'
    )
    
    class Meta:
        model = AttendanceConfiguration
        fields = [
            'section', 'auto_generate_reports',
            'min_attendance_percentage', 'min_attendance_percentage_gte',
            'min_attendance_percentage_lte'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(section__name__icontains=value) |
            Q(section__class_level__name__icontains=value)
        )


class AttendanceSummaryFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    
    # Primary key filter (student is OneToOneField as primary key)
    student = filters.NumberFilter(field_name='student__id')
    
    # Year filter
    current_year = filters.NumberFilter(field_name='current_year')
    
    # Percentage range filters
    overall_percentage_min = filters.NumberFilter(
        field_name='overall_percentage',
        lookup_expr='gte'
    )
    overall_percentage_max = filters.NumberFilter(
        field_name='overall_percentage',
        lookup_expr='lte'
    )
    
    # Streak filters
    current_streak_min = filters.NumberFilter(
        field_name='current_streak',
        lookup_expr='gte'
    )
    current_streak_max = filters.NumberFilter(
        field_name='current_streak',
        lookup_expr='lte'
    )
    
    # Custom filter for needs improvement (below threshold)
    needs_improvement = filters.BooleanFilter(method='filter_needs_improvement')
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'student', 'current_year',
            'overall_percentage_min', 'overall_percentage_max',
            'current_streak_min', 'current_streak_max',
            'needs_improvement'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value)
        )
    
    def filter_needs_improvement(self, queryset, name, value):
        """Filter students who need attendance improvement (below 75%)"""
        if value is True:
            return queryset.filter(overall_percentage__lt=75)
        elif value is False:
            return queryset.filter(overall_percentage__gte=75)
        return queryset