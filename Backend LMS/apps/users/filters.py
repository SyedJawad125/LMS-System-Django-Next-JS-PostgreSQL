import django_filters as filters
from django.db.models import Q
from .models import Employee, Parent, Role, Student, Teacher


class EmployeeFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Employee
        fields = ['status', 'created_at', 'user']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__full_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__mobile__icontains=value) |
            Q(user__role__name__icontains=value)
        )


class RoleFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Role
        fields = ['created_at']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code_name__icontains=value)
        )
    


from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Student, Teacher, Parent


class StudentFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    gender = filters.CharFilter(field_name='gender', lookup_expr='iexact')
    # Removed class_enrolled, section, academic_year filters
    is_hostel_resident = filters.BooleanFilter(field_name='is_hostel_resident')
    is_transport_required = filters.BooleanFilter(field_name='is_transport_required')
    admission_date_from = filters.DateFilter(field_name='admission_date', lookup_expr='gte')
    admission_date_to = filters.DateFilter(field_name='admission_date', lookup_expr='lte')

    class Meta:
        model = Student
        fields = ['status', 'gender', 'is_hostel_resident', 'is_transport_required', 'admission_date']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__full_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__mobile__icontains=value) |
            Q(admission_number__icontains=value) |
            Q(roll_number__icontains=value) |
            Q(nationality__icontains=value)
        )


class TeacherFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    # Removed department filter
    is_class_teacher = filters.BooleanFilter(field_name='is_class_teacher')
    designation = filters.CharFilter(field_name='designation', lookup_expr='icontains')
    joining_date_from = filters.DateFilter(field_name='joining_date', lookup_expr='gte')
    joining_date_to = filters.DateFilter(field_name='joining_date', lookup_expr='lte')
    experience_years_min = filters.NumberFilter(field_name='experience_years', lookup_expr='gte')
    experience_years_max = filters.NumberFilter(field_name='experience_years', lookup_expr='lte')

    class Meta:
        model = Teacher
        fields = ['is_class_teacher', 'designation', 'joining_date', 'experience_years']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__full_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__mobile__icontains=value) |
            Q(employee_id__icontains=value) |
            Q(qualification__icontains=value) |
            Q(specialization__icontains=value) |
            Q(designation__icontains=value)
        )


class ParentFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    relation = filters.CharFilter(field_name='relation', lookup_expr='iexact')
    student = filters.NumberFilter(field_name='students__id')
    occupation = filters.CharFilter(field_name='occupation', lookup_expr='icontains')

    class Meta:
        model = Parent
        fields = ['relation', 'students', 'occupation']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__full_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__mobile__icontains=value) |
            Q(occupation__icontains=value) |
            Q(students__user__full_name__icontains=value) |
            Q(students__admission_number__icontains=value)
        ).distinct()