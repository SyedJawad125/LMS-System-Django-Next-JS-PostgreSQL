from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Route, Vehicle, TransportAllocation


# ==================== Route Filters ====================

class RouteFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    min_distance = filters.NumberFilter(field_name='distance', lookup_expr='gte')
    max_distance = filters.NumberFilter(field_name='distance', lookup_expr='lte')
    min_fee = filters.NumberFilter(field_name='monthly_fee', lookup_expr='gte')
    max_fee = filters.NumberFilter(field_name='monthly_fee', lookup_expr='lte')
    start_point = filters.CharFilter(field_name='start_point', lookup_expr='icontains')
    end_point = filters.CharFilter(field_name='end_point', lookup_expr='icontains')
    
    class Meta:
        model = Route
        fields = ['code', 'start_point', 'end_point']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(start_point__icontains=value) |
            Q(end_point__icontains=value) |
            Q(description__icontains=value)
        )


# ==================== Vehicle Filters ====================

class VehicleFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    vehicle_number = filters.CharFilter(field_name='vehicle_number', lookup_expr='icontains')
    vehicle_model = filters.CharFilter(field_name='vehicle_model', lookup_expr='icontains')
    driver_name = filters.CharFilter(field_name='driver_name', lookup_expr='icontains')
    route = filters.NumberFilter(field_name='route__id')
    route_name = filters.CharFilter(field_name='route__name', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    min_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    insurance_status = filters.CharFilter(method='filter_insurance_status')
    fitness_status = filters.CharFilter(method='filter_fitness_status')
    
    class Meta:
        model = Vehicle
        fields = ['vehicle_number', 'vehicle_model', 'driver_name', 'route', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(vehicle_number__icontains=value) |
            Q(vehicle_model__icontains=value) |
            Q(driver_name__icontains=value) |
            Q(driver_phone__icontains=value) |
            Q(driver_license__icontains=value) |
            Q(route__name__icontains=value)
        )
    
    def filter_insurance_status(self, queryset, name, value):
        """Filter vehicles by insurance status: valid, expiring_soon, expired"""
        from datetime import date, timedelta
        today = date.today()
        thirty_days_later = today + timedelta(days=30)
        
        if value == 'expired':
            return queryset.filter(insurance_expiry__lt=today)
        elif value == 'expiring_soon':
            return queryset.filter(insurance_expiry__gte=today, insurance_expiry__lte=thirty_days_later)
        elif value == 'valid':
            return queryset.filter(insurance_expiry__gt=thirty_days_later)
        return queryset
    
    def filter_fitness_status(self, queryset, name, value):
        """Filter vehicles by fitness status: valid, expiring_soon, expired"""
        from datetime import date, timedelta
        today = date.today()
        thirty_days_later = today + timedelta(days=30)
        
        if value == 'expired':
            return queryset.filter(fitness_expiry__lt=today)
        elif value == 'expiring_soon':
            return queryset.filter(fitness_expiry__gte=today, fitness_expiry__lte=thirty_days_later)
        elif value == 'valid':
            return queryset.filter(fitness_expiry__gt=thirty_days_later)
        return queryset


# ==================== Transport Allocation Filters ====================

class TransportAllocationFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    student = filters.NumberFilter(field_name='student__id')
    student_admission = filters.CharFilter(field_name='student__admission_number', lookup_expr='icontains')
    student_name = filters.CharFilter(method='filter_student_name')
    route = filters.NumberFilter(field_name='route__id')
    route_name = filters.CharFilter(field_name='route__name', lookup_expr='icontains')
    vehicle = filters.NumberFilter(field_name='vehicle__id')
    vehicle_number = filters.CharFilter(field_name='vehicle__vehicle_number', lookup_expr='icontains')
    academic_year = filters.NumberFilter(field_name='academic_year__id')
    academic_year_name = filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    allocation_status = filters.CharFilter(method='filter_allocation_status')
    pickup_point = filters.CharFilter(field_name='pickup_point', lookup_expr='icontains')
    drop_point = filters.CharFilter(field_name='drop_point', lookup_expr='icontains')
    start_date = filters.DateFilter(field_name='start_date')
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date = filters.DateFilter(field_name='end_date')
    end_date_from = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    class Meta:
        model = TransportAllocation
        fields = [
            'student', 'route', 'vehicle', 'academic_year', 
            'is_active', 'pickup_point', 'drop_point'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__username__icontains=value) |
            Q(student__admission_number__icontains=value) |
            Q(student__roll_number__icontains=value) |
            Q(route__name__icontains=value) |
            Q(route__code__icontains=value) |
            Q(vehicle__vehicle_number__icontains=value) |
            Q(pickup_point__icontains=value) |
            Q(drop_point__icontains=value)
        )
    
    def filter_student_name(self, queryset, name, value):
        """Filter by student's full name (first name or last name)"""
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__username__icontains=value)
        )
    
    def filter_allocation_status(self, queryset, name, value):
        """Filter by allocation status: scheduled, active, expired, inactive"""
        from datetime import date
        today = date.today()
        
        if value == 'inactive':
            return queryset.filter(is_active=False)
        elif value == 'scheduled':
            return queryset.filter(is_active=True, start_date__gt=today)
        elif value == 'expired':
            return queryset.filter(is_active=True, end_date__lt=today)
        elif value == 'active':
            return queryset.filter(
                Q(is_active=True, start_date__lte=today) &
                (Q(end_date__isnull=True) | Q(end_date__gte=today))
            )
        return queryset