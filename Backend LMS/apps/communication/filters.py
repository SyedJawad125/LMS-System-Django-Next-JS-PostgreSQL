import django_filters as filters
from django.db.models import Q
from .models import Announcement, Event, Message, Notification


class AnnouncementFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    announcement_type = filters.CharFilter(field_name='announcement_type')
    target_audience = filters.CharFilter(field_name='target_audience')
    is_active = filters.BooleanFilter(field_name='is_active')
    published_by = filters.NumberFilter(field_name='published_by')
    start_date = filters.DateFilter(field_name='published_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='published_at', lookup_expr='lte')
    
    class Meta:
        model = Announcement
        fields = ['title', 'announcement_type', 'target_audience', 'is_active', 'published_by']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(content__icontains=value)
        )


class EventFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    event_type = filters.CharFilter(field_name='event_type')
    is_published = filters.BooleanFilter(field_name='is_published')
    organizer = filters.NumberFilter(field_name='organizer')
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'is_published', 'organizer']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(venue__icontains=value)
        )


class MessageFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    subject = filters.CharFilter(field_name='subject', lookup_expr='icontains')
    sender = filters.NumberFilter(field_name='sender')
    recipient = filters.NumberFilter(field_name='recipient')
    is_read = filters.BooleanFilter(field_name='is_read')
    start_date = filters.DateFilter(field_name='sent_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='sent_at', lookup_expr='lte')
    
    class Meta:
        model = Message
        fields = ['subject', 'sender', 'recipient', 'is_read']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(subject__icontains=value) |
            Q(body__icontains=value)
        )


class NotificationFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    notification_type = filters.CharFilter(field_name='notification_type')
    student = filters.NumberFilter(field_name='student')
    is_read = filters.BooleanFilter(field_name='is_read')
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Notification
        fields = ['title', 'notification_type', 'student', 'is_read']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(message__icontains=value)
        )