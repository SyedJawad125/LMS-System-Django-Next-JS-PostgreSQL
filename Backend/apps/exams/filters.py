from django_filters import rest_framework as filters
from django.db.models import Q

from apps.academic import models
from .models import ExamType, Exam, ExamSchedule, ExamResult, GradeSystem


class ExamTypeFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    min_weightage = filters.NumberFilter(field_name='weightage', lookup_expr='gte')
    max_weightage = filters.NumberFilter(field_name='weightage', lookup_expr='lte')
    
    class Meta:
        model = ExamType
        fields = ['name', 'code', 'weightage']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )


class ExamFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    exam_type = filters.NumberFilter(field_name='exam_type__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    class_level = filters.NumberFilter(field_name='class_level__id')
    is_published = filters.BooleanFilter(field_name='is_published')
    
    # Date range filters
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Additional useful filters
    exam_type_code = filters.CharFilter(field_name='exam_type__code', lookup_expr='iexact')
    class_name = filters.CharFilter(field_name='class_level__name', lookup_expr='icontains')
    current_year = filters.BooleanFilter(method='filter_current_year')
    
    class Meta:
        model = Exam
        fields = [
            'name', 'exam_type', 'academic_year', 'class_level', 
            'is_published', 'start_date', 'end_date'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(exam_type__name__icontains=value) |
            Q(exam_type__code__icontains=value) |
            Q(class_level__name__icontains=value) |
            Q(academic_year__name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_current_year(self, queryset, name, value):
        if value:
            return queryset.filter(academic_year__is_active=True)
        return queryset


class ExamScheduleFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    exam = filters.NumberFilter(field_name='exam__id')
    subject = filters.NumberFilter(field_name='subject__id')
    room = filters.CharFilter(field_name='room', lookup_expr='icontains')
    
    # Date and time filters
    date = filters.DateFilter(field_name='date')
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Related filters
    exam_type = filters.NumberFilter(field_name='exam__exam_type__id')
    class_level = filters.NumberFilter(field_name='exam__class_level__id')
    academic_year = filters.NumberFilter(field_name='exam__academic_year__id')
    is_published = filters.BooleanFilter(field_name='exam__is_published')
    
    # Marks filters
    min_marks = filters.NumberFilter(field_name='max_marks', lookup_expr='gte')
    max_marks = filters.NumberFilter(field_name='max_marks', lookup_expr='lte')
    
    class Meta:
        model = ExamSchedule
        fields = [
            'exam', 'subject', 'date', 'room', 
            'max_marks', 'min_passing_marks'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(exam__name__icontains=value) |
            Q(subject__name__icontains=value) |
            Q(subject__code__icontains=value) |
            Q(room__icontains=value) |
            Q(exam__exam_type__name__icontains=value)
        )


class ExamResultFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    exam_schedule = filters.NumberFilter(field_name='exam_schedule__id')
    student = filters.NumberFilter(field_name='student__id')
    grade = filters.CharFilter(field_name='grade', lookup_expr='iexact')
    is_absent = filters.BooleanFilter(field_name='is_absent')
    entered_by = filters.NumberFilter(field_name='entered_by__id')
    
    # Marks filters
    min_marks = filters.NumberFilter(field_name='marks_obtained', lookup_expr='gte')
    max_marks = filters.NumberFilter(field_name='marks_obtained', lookup_expr='lte')
    
    # Related filters
    exam = filters.NumberFilter(field_name='exam_schedule__exam__id')
    subject = filters.NumberFilter(field_name='exam_schedule__subject__id')
    class_level = filters.NumberFilter(field_name='exam_schedule__exam__class_level__id')
    academic_year = filters.NumberFilter(field_name='exam_schedule__exam__academic_year__id')
    exam_type = filters.NumberFilter(field_name='exam_schedule__exam__exam_type__id')
    
    # Student related filters
    student_roll_number = filters.CharFilter(field_name='student__roll_number', lookup_expr='icontains')
    student_class = filters.NumberFilter(field_name='student__current_class__id')
    
    # Performance filters
    passed = filters.BooleanFilter(method='filter_passed')
    failed = filters.BooleanFilter(method='filter_failed')
    
    # Date filters
    entered_date = filters.DateFilter(field_name='entered_at__date')
    entered_from = filters.DateFilter(field_name='entered_at__date', lookup_expr='gte')
    entered_to = filters.DateFilter(field_name='entered_at__date', lookup_expr='lte')
    
    class Meta:
        model = ExamResult
        fields = [
            'exam_schedule', 'student', 'grade', 'is_absent', 
            'entered_by', 'marks_obtained'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__full_name__icontains=value) |
            Q(student__roll_number__icontains=value) |
            Q(student__admission_number__icontains=value) |
            Q(exam_schedule__exam__name__icontains=value) |
            Q(exam_schedule__subject__name__icontains=value) |
            Q(grade__icontains=value) |
            Q(entered_by__user__full_name__icontains=value)
        )
    
    def filter_passed(self, queryset, name, value):
        if value:
            return queryset.filter(
                marks_obtained__gte=models.F('exam_schedule__min_passing_marks'),
                is_absent=False
            )
        return queryset
    
    def filter_failed(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(marks_obtained__lt=models.F('exam_schedule__min_passing_marks')) |
                Q(is_absent=True)
            )
        return queryset


class GradeSystemFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    grade = filters.CharFilter(field_name='grade', lookup_expr='iexact')
    
    # Percentage range filters
    min_percentage = filters.NumberFilter(field_name='min_percentage', lookup_expr='gte')
    max_percentage = filters.NumberFilter(field_name='max_percentage', lookup_expr='lte')
    percentage = filters.NumberFilter(method='filter_percentage')
    
    # Grade point filters
    min_grade_point = filters.NumberFilter(field_name='grade_point', lookup_expr='gte')
    max_grade_point = filters.NumberFilter(field_name='grade_point', lookup_expr='lte')
    
    class Meta:
        model = GradeSystem
        fields = [
            'name', 'grade', 'min_percentage', 
            'max_percentage', 'grade_point'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(grade__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_percentage(self, queryset, name, value):
        """Filter grades that match a specific percentage"""
        return queryset.filter(
            min_percentage__lte=value,
            max_percentage__gte=value
        )