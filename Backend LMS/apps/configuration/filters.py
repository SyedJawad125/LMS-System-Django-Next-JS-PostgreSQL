from django_filters import rest_framework as filters
from django.db.models import Q
from .models import SchoolSettings, EmailTemplate, SMSTemplate, AuditLog


class SchoolSettingsFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    school_name = filters.CharFilter(field_name='school_name', lookup_expr='icontains')
    school_code = filters.CharFilter(field_name='school_code', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    phone = filters.CharFilter(field_name='phone', lookup_expr='icontains')
    website = filters.CharFilter(field_name='website', lookup_expr='icontains')
    principal_name = filters.CharFilter(field_name='principal_name', lookup_expr='icontains')
    currency = filters.CharFilter(field_name='currency', lookup_expr='iexact')
    timezone = filters.CharFilter(field_name='timezone', lookup_expr='icontains')
    min_established_year = filters.NumberFilter(field_name='established_year', lookup_expr='gte')
    max_established_year = filters.NumberFilter(field_name='established_year', lookup_expr='lte')
    academic_year_start_month = filters.NumberFilter(field_name='academic_year_start_month')
    
    class Meta:
        model = SchoolSettings
        fields = [
            'school_name', 'school_code', 'email', 'phone', 
            'principal_name', 'currency', 'timezone', 'academic_year_start_month'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(school_name__icontains=value) |
            Q(school_code__icontains=value) |
            Q(email__icontains=value) |
            Q(principal_name__icontains=value) |
            Q(address__icontains=value) |
            Q(website__icontains=value)
        )


class EmailTemplateFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    subject = filters.CharFilter(field_name='subject', lookup_expr='icontains')
    template_type = filters.CharFilter(field_name='template_type', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    
    # Date filters (assuming TimeUserStamps has created_at and updated_at)
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        model = EmailTemplate
        fields = ['name', 'template_type', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(subject__icontains=value) |
            Q(body__icontains=value) |
            Q(template_type__icontains=value)
        )


class SMSTemplateFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    message = filters.CharFilter(field_name='message', lookup_expr='icontains')
    template_type = filters.CharFilter(field_name='template_type', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    
    # Date filters
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        model = SMSTemplate
        fields = ['name', 'template_type', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(message__icontains=value) |
            Q(template_type__icontains=value)
        )


class AuditLogFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    action = filters.CharFilter(field_name='action', lookup_expr='icontains')
    model_name = filters.CharFilter(field_name='model_name', lookup_expr='icontains')
    object_id = filters.CharFilter(field_name='object_id', lookup_expr='icontains')
    ip_address = filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    
    # Date filters
    start_date = filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='timestamp', lookup_expr='lte')
    start_datetime = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_datetime = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # User ID filter
    user_id = filters.NumberFilter(field_name='user__id')
    
    # Action type filters (common patterns)
    action_type = filters.ChoiceFilter(
        field_name='action',
        choices=[
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
            ('view', 'View'),
            ('login', 'Login'),
            ('logout', 'Logout'),
        ],
        lookup_expr='icontains'
    )
    
    class Meta:
        model = AuditLog
        fields = [
            'user', 'action', 'model_name', 'object_id', 
            'ip_address', 'timestamp'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(action__icontains=value) |
            Q(model_name__icontains=value) |
            Q(object_id__icontains=value) |
            Q(ip_address__icontains=value) |
            Q(changes__icontains=value)  # JSONField might need special handling
        )