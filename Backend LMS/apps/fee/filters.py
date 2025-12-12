import django_filters as filters
from django.db.models import Q
from .models import (
    FeeType, FeeStructure, FeeInvoice, FeeInvoiceItem, 
    FeePayment, FeeDiscount, StudentDiscount
)

class FeeTypeFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    is_recurring = filters.BooleanFilter(field_name='is_recurring')
    
    class Meta:
        model = FeeType
        fields = ['code', 'is_recurring']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )


class FeeStructureFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    class_level = filters.NumberFilter(field_name='class_level__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    fee_type = filters.NumberFilter(field_name='fee_type__id')
    frequency = filters.ChoiceFilter(choices=FeeStructure._meta.get_field('frequency').choices)
    
    # Additional useful filters
    class_level_name = filters.CharFilter(field_name='class_level__name', lookup_expr='icontains')
    academic_year_name = filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    fee_type_name = filters.CharFilter(field_name='fee_type__name', lookup_expr='icontains')
    
    class Meta:
        model = FeeStructure
        fields = ['class_level', 'academic_year', 'fee_type', 'frequency']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(class_level__name__icontains=value) |
            Q(academic_year__name__icontains=value) |
            Q(fee_type__name__icontains=value) |
            Q(fee_type__code__icontains=value)
        )


class FeeInvoiceFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    student = filters.NumberFilter(field_name='student__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    month = filters.NumberFilter(field_name='month')
    year = filters.NumberFilter(field_name='year')
    status = filters.ChoiceFilter(choices=FeeInvoice.STATUS_CHOICES)
    due_date = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
    
    # Additional useful filters
    student_name = filters.CharFilter(method='filter_student_name')
    student_admission_no = filters.CharFilter(field_name='student__admission_number', lookup_expr='icontains')
    invoice_number = filters.CharFilter(field_name='invoice_number', lookup_expr='icontains')
    
    class Meta:
        model = FeeInvoice
        fields = [
            'student', 'academic_year', 'month', 'year', 'status',
            'due_date', 'created_at'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(invoice_number__icontains=value) |
            Q(student__user__full_name__icontains=value) |
            Q(student__admission_number__icontains=value) |
            Q(academic_year__name__icontains=value)
        )
    
    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )


class FeeInvoiceItemFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    invoice = filters.NumberFilter(field_name='invoice__id')
    fee_type = filters.NumberFilter(field_name='fee_type__id')
    
    # Additional useful filters
    invoice_number = filters.CharFilter(field_name='invoice__invoice_number', lookup_expr='icontains')
    fee_type_name = filters.CharFilter(field_name='fee_type__name', lookup_expr='icontains')
    
    class Meta:
        model = FeeInvoiceItem
        fields = ['invoice', 'fee_type']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(invoice__invoice_number__icontains=value) |
            Q(fee_type__name__icontains=value) |
            Q(fee_type__code__icontains=value) |
            Q(description__icontains=value)
        )


class FeePaymentFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    invoice = filters.NumberFilter(field_name='invoice__id')
    payment_method = filters.ChoiceFilter(choices=FeePayment.PAYMENT_METHODS)
    payment_date = filters.DateFromToRangeFilter()
    received_by = filters.NumberFilter(field_name='received_by__id')
    
    # Additional useful filters
    payment_id = filters.CharFilter(field_name='payment_id', lookup_expr='icontains')
    invoice_number = filters.CharFilter(field_name='invoice__invoice_number', lookup_expr='icontains')
    student_name = filters.CharFilter(method='filter_student_name')
    transaction_reference = filters.CharFilter(field_name='transaction_reference', lookup_expr='icontains')
    
    class Meta:
        model = FeePayment
        fields = ['invoice', 'payment_method', 'payment_date', 'received_by']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(payment_id__icontains=value) |
            Q(invoice__invoice_number__icontains=value) |
            Q(invoice__student__user__full_name__icontains=value) |
            Q(transaction_reference__icontains=value) |
            Q(remarks__icontains=value)
        )
    
    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(invoice__student__user__first_name__icontains=value) |
            Q(invoice__student__user__last_name__icontains=value) |
            Q(invoice__student__user__full_name__icontains=value)
        )


class FeeDiscountFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    discount_type = filters.ChoiceFilter(choices=FeeDiscount.DISCOUNT_TYPES)
    is_active = filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = FeeDiscount
        fields = ['discount_type', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class StudentDiscountFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    student = filters.NumberFilter(field_name='student__id')
    discount = filters.NumberFilter(field_name='discount__id')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    approved_by = filters.NumberFilter(field_name='approved_by__id')
    start_date = filters.DateFromToRangeFilter()
    end_date = filters.DateFromToRangeFilter()
    
    # Additional useful filters
    student_name = filters.CharFilter(method='filter_student_name')
    student_admission_no = filters.CharFilter(field_name='student__admission_number', lookup_expr='icontains')
    discount_name = filters.CharFilter(field_name='discount__name', lookup_expr='icontains')
    
    class Meta:
        model = StudentDiscount
        fields = ['student', 'discount', 'academic_year', 'approved_by', 'start_date', 'end_date']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__full_name__icontains=value) |
            Q(student__admission_number__icontains=value) |
            Q(discount__name__icontains=value) |
            Q(remarks__icontains=value)
        )
    
    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )