from django.db import models

from apps.academic.models import AcademicYear
from apps.users.models import Student
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class Route(TimeUserStamps):
    """Transport Routes"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True)  # Make blank=True for auto-generation
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    distance = models.DecimalField(max_digits=6, decimal_places=2)  # in KM
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'routes'
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Generate code automatically when not provided
            self.code = self.generate_route_code()
        super().save(*args, **kwargs)
    
    def generate_route_code(self):
        """Generate unique route code like RT001, RT002, etc."""
        from django.db.models import Max
        # Get the highest existing code number
        max_code = Route.objects.filter(code__regex=r'^RT\d+$').aggregate(Max('code'))
        if max_code['code__max']:
            # Extract number and increment
            last_number = int(max_code['code__max'][2:])  # Remove 'RT' prefix
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"RT{new_number:03d}"  # Format as RT001, RT002, etc.


class Vehicle(TimeUserStamps):
    """School Vehicles"""
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_model = models.CharField(max_length=100)
    capacity = models.IntegerField()
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    driver_license = models.CharField(max_length=50)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    insurance_expiry = models.DateField()
    fitness_expiry = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'vehicles'


class TransportAllocation(TimeUserStamps):
    """Student Transport Allocation"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport')
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    pickup_point = models.CharField(max_length=200)
    drop_point = models.CharField(max_length=200)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'transport_allocations'