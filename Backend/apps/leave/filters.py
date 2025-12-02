import django_filters as filters
from django.db.models import Q
from django.utils import timezone
from .models import (
    LeaveType, LeaveApplication, LeaveBalance,
    LeaveConfiguration, LeaveApprovalWorkflow, LeaveHistory
)


class LeaveTypeFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    requires_approval = filters.BooleanFilter(field_name='requires_approval')
    is_active = filters.BooleanFilter(field_name='is_active')
    max_days_per_year = filters.NumberFilter(field_name='max_days_per_year')
    max_days_per_year__gt = filters.NumberFilter(field_name='max_days_per_year', lookup_expr='gt')
    max_days_per_year__lt = filters.NumberFilter(field_name='max_days_per_year', lookup_expr='lt')
    
    class Meta:
        model = LeaveType
        fields = ['code', 'name', 'requires_approval', 'is_active', 'max_days_per_year']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )


class LeaveApplicationFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    application_number = filters.CharFilter(field_name='application_number', lookup_expr='icontains')
    teacher = filters.NumberFilter(field_name='teacher_id')
    student = filters.NumberFilter(field_name='student_id')
    leave_type = filters.NumberFilter(field_name='leave_type_id')
    leave_type_name = filters.CharFilter(field_name='leave_type__name', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status')
    status__in = filters.BaseInFilter(field_name='status', lookup_expr='in')
    start_date = filters.DateFilter(field_name='start_date')
    start_date__gte = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date__lte = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date = filters.DateFilter(field_name='end_date')
    end_date__gte = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date__lte = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    total_days = filters.NumberFilter(field_name='total_days')
    total_days__gt = filters.NumberFilter(field_name='total_days', lookup_expr='gt')
    total_days__lt = filters.NumberFilter(field_name='total_days', lookup_expr='lt')
    reviewed_by = filters.NumberFilter(field_name='reviewed_by_id')
    applied_at = filters.DateFilter(field_name='applied_at')
    applied_at__gte = filters.DateFilter(field_name='applied_at', lookup_expr='gte')
    applied_at__lte = filters.DateFilter(field_name='applied_at', lookup_expr='lte')
    reviewed_at = filters.DateFilter(field_name='reviewed_at')
    reviewed_at__gte = filters.DateFilter(field_name='reviewed_at', lookup_expr='gte')
    reviewed_at__lte = filters.DateFilter(field_name='reviewed_at', lookup_expr='lte')
    academic_year = filters.NumberFilter(method='filter_academic_year')
    is_pending = filters.BooleanFilter(method='filter_is_pending')
    is_approved = filters.BooleanFilter(method='filter_is_approved')
    
    class Meta:
        model = LeaveApplication
        fields = [
            'application_number', 'teacher', 'student', 'leave_type',
            'status', 'start_date', 'end_date', 'reviewed_by'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(application_number__icontains=value) |
            Q(reason__icontains=value) |
            Q(remarks__icontains=value) |
            Q(teacher__user__first_name__icontains=value) |
            Q(teacher__user__last_name__icontains=value) |
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(leave_type__name__icontains=value)
        )
    
    def filter_academic_year(self, queryset, name, value):
        return queryset.filter(
            Q(start_date__year=value) |
            Q(end_date__year=value)
        ).distinct()
    
    def filter_is_pending(self, queryset, name, value):
        from utils.enums import PENDING
        if value:
            return queryset.filter(status=PENDING)
        return queryset.exclude(status=PENDING)
    
    def filter_is_approved(self, queryset, name, value):
        from utils.enums import APPROVED
        if value:
            return queryset.filter(status=APPROVED)
        return queryset.exclude(status=APPROVED)


class LeaveBalanceFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    teacher = filters.NumberFilter(field_name='teacher_id')
    student = filters.NumberFilter(field_name='student_id')
    leave_type = filters.NumberFilter(field_name='leave_type_id')
    leave_type_name = filters.CharFilter(field_name='leave_type__name', lookup_expr='icontains')
    academic_year = filters.NumberFilter(field_name='academic_year')
    academic_year__in = filters.BaseInFilter(field_name='academic_year', lookup_expr='in')
    total_allocated = filters.NumberFilter(field_name='total_allocated')
    total_allocated__gt = filters.NumberFilter(field_name='total_allocated', lookup_expr='gt')
    total_allocated__lt = filters.NumberFilter(field_name='total_allocated', lookup_expr='lt')
    used = filters.NumberFilter(field_name='used')
    used__gt = filters.NumberFilter(field_name='used', lookup_expr='gt')
    used__lt = filters.NumberFilter(field_name='used', lookup_expr='lt')
    remaining = filters.NumberFilter(field_name='remaining')
    remaining__gt = filters.NumberFilter(field_name='remaining', lookup_expr='gt')
    remaining__lt = filters.NumberFilter(field_name='remaining', lookup_expr='lt')
    remaining_zero = filters.BooleanFilter(method='filter_remaining_zero')
    carried_over = filters.NumberFilter(field_name='carried_over')
    carried_over__gt = filters.NumberFilter(field_name='carried_over', lookup_expr='gt')
    
    class Meta:
        model = LeaveBalance
        fields = [
            'teacher', 'student', 'leave_type', 'academic_year',
            'total_allocated', 'used', 'remaining', 'carried_over'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(teacher__user__first_name__icontains=value) |
            Q(teacher__user__last_name__icontains=value) |
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(leave_type__name__icontains=value) |
            Q(leave_type__code__icontains=value)
        )
    
    def filter_remaining_zero(self, queryset, name, value):
        if value:
            return queryset.filter(remaining=0)
        return queryset.filter(remaining__gt=0)


class LeaveConfigurationFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    academic_year = filters.NumberFilter(field_name='academic_year')
    academic_year__in = filters.BaseInFilter(field_name='academic_year', lookup_expr='in')
    max_consecutive_days = filters.NumberFilter(field_name='max_consecutive_days')
    advance_notice_days = filters.NumberFilter(field_name='advance_notice_days')
    max_advance_days = filters.NumberFilter(field_name='max_advance_days')
    require_multilevel_approval = filters.BooleanFilter(field_name='require_multilevel_approval')
    auto_approve_short_leaves = filters.BooleanFilter(field_name='auto_approve_short_leaves')
    auto_approve_max_days = filters.NumberFilter(field_name='auto_approve_max_days')
    allow_carry_over = filters.BooleanFilter(field_name='allow_carry_over')
    max_carry_over_days = filters.NumberFilter(field_name='max_carry_over_days')
    carry_over_validity_months = filters.NumberFilter(field_name='carry_over_validity_months')
    notify_applicant_on_status_change = filters.BooleanFilter(field_name='notify_applicant_on_status_change')
    notify_reviewer_on_new_application = filters.BooleanFilter(field_name='notify_reviewer_on_new_application')
    is_active = filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = LeaveConfiguration
        fields = [
            'academic_year', 'max_consecutive_days', 'advance_notice_days',
            'max_advance_days', 'require_multilevel_approval',
            'auto_approve_short_leaves', 'allow_carry_over', 'is_active'
        ]
    
    def filter_search(self, queryset, name, value):
        # Since configuration doesn't have many text fields, search by academic year
        try:
            year = int(value)
            return queryset.filter(academic_year=year)
        except ValueError:
            return queryset.none()


class LeaveApprovalWorkflowFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    leave_application = filters.NumberFilter(field_name='leave_application_id')
    leave_application_number = filters.CharFilter(field_name='leave_application__application_number', lookup_expr='icontains')
    approval_level = filters.NumberFilter(field_name='approval_level')
    approval_level__in = filters.BaseInFilter(field_name='approval_level', lookup_expr='in')
    approver = filters.NumberFilter(field_name='approver_id')
    status = filters.CharFilter(field_name='status')
    status__in = filters.BaseInFilter(field_name='status', lookup_expr='in')
    is_current_level = filters.BooleanFilter(field_name='is_current_level')
    approved_at = filters.DateFilter(field_name='approved_at')
    approved_at__gte = filters.DateFilter(field_name='approved_at', lookup_expr='gte')
    approved_at__lte = filters.DateFilter(field_name='approved_at', lookup_expr='lte')
    deadline = filters.DateFilter(field_name='deadline')
    deadline__gte = filters.DateFilter(field_name='deadline', lookup_expr='gte')
    deadline__lte = filters.DateFilter(field_name='deadline', lookup_expr='lte')
    overdue = filters.BooleanFilter(method='filter_overdue')
    applicant_type = filters.CharFilter(method='filter_applicant_type')
    applicant_name = filters.CharFilter(method='filter_applicant_name')
    
    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'leave_application', 'approval_level', 'approver',
            'status', 'is_current_level', 'deadline'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(leave_application__application_number__icontains=value) |
            Q(comments__icontains=value) |
            Q(approver__user__first_name__icontains=value) |
            Q(approver__user__last_name__icontains=value) |
            Q(leave_application__teacher__user__first_name__icontains=value) |
            Q(leave_application__teacher__user__last_name__icontains=value) |
            Q(leave_application__student__user__first_name__icontains=value) |
            Q(leave_application__student__user__last_name__icontains=value)
        )
    
    def filter_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(
                deadline__lt=timezone.now(),
                status__in=['PENDING']  # You might need to import PENDING from enums
            )
        return queryset
    
    def filter_applicant_type(self, queryset, name, value):
        if value == 'teacher':
            return queryset.filter(leave_application__teacher__isnull=False)
        elif value == 'student':
            return queryset.filter(leave_application__student__isnull=False)
        return queryset
    
    def filter_applicant_name(self, queryset, name, value):
        return queryset.filter(
            Q(leave_application__teacher__user__first_name__icontains=value) |
            Q(leave_application__teacher__user__last_name__icontains=value) |
            Q(leave_application__student__user__first_name__icontains=value) |
            Q(leave_application__student__user__last_name__icontains=value)
        )


class LeaveHistoryFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    leave_application = filters.NumberFilter(field_name='leave_application_id')
    leave_application_number = filters.CharFilter(field_name='leave_application__application_number', lookup_expr='icontains')
    action = filters.CharFilter(field_name='action', lookup_expr='icontains')
    changed_by = filters.NumberFilter(field_name='changed_by_id')
    previous_status = filters.CharFilter(field_name='previous_status')
    new_status = filters.CharFilter(field_name='new_status')
    created_at = filters.DateFilter(field_name='created_at')
    created_at__gte = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    ip_address = filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    action_type = filters.CharFilter(method='filter_action_type')
    date_range = filters.DateRangeFilter(field_name='created_at')
    
    class Meta:
        model = LeaveHistory
        fields = [
            'leave_application', 'action', 'changed_by',
            'previous_status', 'new_status', 'created_at'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(leave_application__application_number__icontains=value) |
            Q(action__icontains=value) |
            Q(changed_by__first_name__icontains=value) |
            Q(changed_by__last_name__icontains=value) |
            Q(changes__icontains=value)
        )
    
    def filter_action_type(self, queryset, name, value):
        actions = {
            'status_change': ['STATUS_CHANGE', 'STATUS_UPDATE'],
            'created': ['CREATED', 'APPLIED'],
            'updated': ['UPDATED', 'MODIFIED'],
            'approved': ['APPROVED'],
            'rejected': ['REJECTED'],
            'cancelled': ['CANCELLED'],
        }
        
        if value in actions:
            return queryset.filter(action__in=actions[value])
        return queryset.filter(action__icontains=value)