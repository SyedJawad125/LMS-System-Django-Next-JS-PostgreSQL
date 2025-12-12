import django_filters as filters
from django.db.models import Q
from .models import AcademicYear, Department, Class, Section, Subject, ClassSubject


class AcademicYearFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    is_current = filters.BooleanFilter(field_name='is_current')
    is_active = filters.BooleanFilter(field_name='is_active')
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = AcademicYear
        fields = ['is_current', 'is_active']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )


class DepartmentFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    code = filters.CharFilter(field_name='code', lookup_expr='iexact')

    class Meta:
        model = Department
        fields = ['code']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )


class ClassFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    level = filters.NumberFilter(field_name='level')
    code = filters.CharFilter(field_name='code', lookup_expr='iexact')

    class Meta:
        model = Class
        fields = ['level', 'code']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )


class SectionFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    class_level = filters.NumberFilter(field_name='class_level__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    class_teacher = filters.NumberFilter(field_name='class_teacher__id')
    room_number = filters.CharFilter(field_name='room_number', lookup_expr='iexact')

    class Meta:
        model = Section
        fields = ['class_level', 'academic_year', 'class_teacher', 'room_number']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(room_number__icontains=value) |
            Q(class_level__name__icontains=value)
        )


class SubjectFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    subject_type = filters.CharFilter(field_name='subject_type', lookup_expr='iexact')
    department = filters.NumberFilter(field_name='department__id')
    code = filters.CharFilter(field_name='code', lookup_expr='iexact')
    credit_hours = filters.NumberFilter(field_name='credit_hours')

    class Meta:
        model = Subject
        fields = ['subject_type', 'department', 'code', 'credit_hours']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value) |
            Q(department__name__icontains=value)
        )


class ClassSubjectFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    class_level = filters.NumberFilter(field_name='class_level__id')
    section = filters.NumberFilter(field_name='section__id')
    subject = filters.NumberFilter(field_name='subject__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    teacher = filters.NumberFilter(field_name='teacher__id')

    class Meta:
        model = ClassSubject
        fields = ['class_level', 'section', 'subject', 'academic_year', 'teacher']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(class_level__name__icontains=value) |
            Q(section__name__icontains=value) |
            Q(subject__name__icontains=value) |
            Q(teacher__user__full_name__icontains=value) |
            Q(academic_year__name__icontains=value)
        )