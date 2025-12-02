from django.db.models import Q
from django_filters import rest_framework as filters

from apps.certificate.models import Certificate, CertificateTemplate, Document



class CertificateTemplateFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    certificate_type = filters.CharFilter(field_name='certificate_type', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = CertificateTemplate
        fields = ['name', 'certificate_type', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(certificate_type__icontains=value) |
            Q(description__icontains=value)
        )


class CertificateFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    certificate_number = filters.CharFilter(field_name='certificate_number', lookup_expr='icontains')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    student = filters.CharFilter(field_name='student__name', lookup_expr='icontains')
    issued_by = filters.CharFilter(field_name='issued_by__name', lookup_expr='icontains')
    min_issue_date = filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    max_issue_date = filters.DateFilter(field_name='issue_date', lookup_expr='lte')
    
    class Meta:
        model = Certificate
        fields = ['certificate_number', 'student', 'title', 'issued_by']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(certificate_number__icontains=value) |
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(student__name__icontains=value) |
            Q(issued_by__name__icontains=value)
        )


class DocumentFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    student = filters.CharFilter(field_name='student__name', lookup_expr='icontains')
    uploaded_by = filters.CharFilter(field_name='uploaded_by__name', lookup_expr='icontains')
    document_type = filters.CharFilter(field_name='document_type', lookup_expr='icontains')
    min_upload_date = filters.DateFilter(field_name='uploaded_at', lookup_expr='gte')
    max_upload_date = filters.DateFilter(field_name='uploaded_at', lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = ['document_type', 'student', 'uploaded_by']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(document_type__icontains=value) |
            Q(student__name__icontains=value) |
            Q(uploaded_by__name__icontains=value)
        )