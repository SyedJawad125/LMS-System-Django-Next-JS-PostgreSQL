import django_filters as filters
from django.db.models import Q
from .models import TimeSlot, Timetable


class TimeSlotFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    is_break = filters.BooleanFilter(field_name='is_break')
    start_time = filters.TimeFilter(field_name='start_time')
    end_time = filters.TimeFilter(field_name='end_time')
    order = filters.NumberFilter(field_name='order')
    
    class Meta:
        model = TimeSlot
        fields = ['is_break', 'start_time', 'end_time', 'order']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )


class TimetableFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    section = filters.NumberFilter(field_name='section__id')
    day = filters.ChoiceFilter(
        field_name='day',
        choices=Timetable.DAYS
    )
    time_slot = filters.NumberFilter(field_name='time_slot__id')
    subject = filters.NumberFilter(field_name='subject__id')
    teacher = filters.NumberFilter(field_name='teacher__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    room = filters.CharFilter(field_name='room', lookup_expr='icontains')
    
    # Additional useful filters
    class_level = filters.NumberFilter(field_name='section__class_level__id')
    section_name = filters.CharFilter(field_name='section__name', lookup_expr='icontains')
    
    class Meta:
        model = Timetable
        fields = [
            'section', 'day', 'time_slot', 'subject', 
            'teacher', 'academic_year', 'room', 'class_level'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(section__name__icontains=value) |
            Q(section__class_level__name__icontains=value) |
            Q(subject__name__icontains=value) |
            Q(teacher__user__full_name__icontains=value) |
            Q(time_slot__name__icontains=value) |
            Q(room__icontains=value) |
            Q(academic_year__name__icontains=value)
        )