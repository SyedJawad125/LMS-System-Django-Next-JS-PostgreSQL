import django_filters as filters
from django.db.models import Q
from .models import ReportCard, StudentBehavior
from apps.academic.models import AcademicYear
from apps.exams.models import Exam
from apps.users.models import Student, Teacher
from utils.enums import *

class ReportCardFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    student = filters.CharFilter(field_name='student__name', lookup_expr='icontains')
    student_id = filters.CharFilter(field_name='student__student_id', lookup_expr='icontains')
    exam = filters.CharFilter(field_name='exam__name', lookup_expr='icontains')
    academic_year = filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    min_percentage = filters.NumberFilter(field_name='percentage', lookup_expr='gte')
    max_percentage = filters.NumberFilter(field_name='percentage', lookup_expr='lte')
    grade = filters.CharFilter(field_name='grade', lookup_expr='iexact')
    min_rank = filters.NumberFilter(field_name='rank_in_class', lookup_expr='gte')
    max_rank = filters.NumberFilter(field_name='rank_in_class', lookup_expr='lte')
    
    class Meta:
        model = ReportCard
        fields = ['student', 'exam', 'academic_year', 'grade']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__name__icontains=value) |
            Q(student__student_id__icontains=value) |
            Q(exam__name__icontains=value) |
            Q(grade__icontains=value) |
            Q(remarks__icontains=value)
        )


class StudentBehaviorFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    student = filters.CharFilter(field_name='student__name', lookup_expr='icontains')
    student_id = filters.CharFilter(field_name='student__student_id', lookup_expr='icontains')
    behavior_type = filters.ChoiceFilter(choices=StudentBehavior.BEHAVIOR_TYPES)
    incident_date = filters.DateFromToRangeFilter()
    reported_by = filters.CharFilter(field_name='reported_by__name', lookup_expr='icontains')
    min_points = filters.NumberFilter(field_name='points', lookup_expr='gte')
    max_points = filters.NumberFilter(field_name='points', lookup_expr='lte')
    created_at = filters.DateFromToRangeFilter()
    
    class Meta:
        model = StudentBehavior
        fields = ['behavior_type', 'student', 'reported_by']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__name__icontains=value) |
            Q(student__student_id__icontains=value) |
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(action_taken__icontains=value) |
            Q(reported_by__name__icontains=value)
        )