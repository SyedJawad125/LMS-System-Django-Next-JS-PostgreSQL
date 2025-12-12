from django_filters import rest_framework as filters
from django.db.models import Q

from utils.enums import *
from .models import Assignment, AssignmentSubmission


class AssignmentFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    subject = filters.NumberFilter(field_name='subject__id')
    class_level = filters.NumberFilter(field_name='class_level__id')
    section = filters.NumberFilter(field_name='section__id')
    teacher = filters.NumberFilter(field_name='teacher__id')
    assign_date_from = filters.DateFilter(field_name='assign_date', lookup_expr='gte')
    assign_date_to = filters.DateFilter(field_name='assign_date', lookup_expr='lte')
    due_date_from = filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    max_marks_min = filters.NumberFilter(field_name='max_marks', lookup_expr='gte')
    max_marks_max = filters.NumberFilter(field_name='max_marks', lookup_expr='lte')
    has_attachment = filters.BooleanFilter(method='filter_has_attachment')
    
    class Meta:
        model = Assignment
        fields = ['subject', 'class_level', 'section', 'teacher']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(instructions__icontains=value)
        )
    
    def filter_has_attachment(self, queryset, name, value):
        if value:
            return queryset.exclude(attachment='')
        return queryset.filter(attachment='')


class AssignmentSubmissionFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    assignment = filters.NumberFilter(field_name='assignment__id')
    student = filters.NumberFilter(field_name='student__id')
    status = filters.ChoiceFilter(choices=AssignmentSubmission.STATUS_CHOICES)
    submission_date_from = filters.DateTimeFilter(field_name='submission_date', lookup_expr='gte')
    submission_date_to = filters.DateTimeFilter(field_name='submission_date', lookup_expr='lte')
    marks_obtained_min = filters.NumberFilter(field_name='marks_obtained', lookup_expr='gte')
    marks_obtained_max = filters.NumberFilter(field_name='marks_obtained', lookup_expr='lte')
    graded_by = filters.NumberFilter(field_name='graded_by__id')
    graded_at_from = filters.DateTimeFilter(field_name='graded_at', lookup_expr='gte')
    graded_at_to = filters.DateTimeFilter(field_name='graded_at', lookup_expr='lte')
    is_graded = filters.BooleanFilter(method='filter_is_graded')
    is_late = filters.BooleanFilter(method='filter_is_late')
    
    class Meta:
        model = AssignmentSubmission
        fields = ['assignment', 'student', 'status', 'graded_by']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(assignment__title__icontains=value) |
            Q(submission_text__icontains=value) |
            Q(feedback__icontains=value)
        )
    
    def filter_is_graded(self, queryset, name, value):
        if value:
            return queryset.filter(status=GRADED)
        return queryset.exclude(status=GRADED)
    
    def filter_is_late(self, queryset, name, value):
        if value:
            return queryset.filter(status=LATE_SUBMISSION)
        return queryset.exclude(status=LATE_SUBMISSION)