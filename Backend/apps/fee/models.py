from django.db import models

from apps.academic.models import AcademicYear, Class
from apps.users.models import Student, User
from utils.reusable_classes import TimeUserStamps
from django.core.validators import MinValueValidator, MaxValueValidator  # Add this import

# Create your models here.

class FeeType(TimeUserStamps):
    """Types of Fees"""
    name = models.CharField(max_length=100)  # Tuition, Transport, Library, etc.
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=True)  # Monthly/Yearly or One-time
    
    class Meta:
        db_table = 'fee_types'


class FeeStructure(TimeUserStamps):
    """Fee Structure for Classes"""
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=(
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ))
    due_date_day = models.IntegerField(default=10)  # Day of month
    
    class Meta:
        db_table = 'fee_structures'
        unique_together = ['class_level', 'academic_year', 'fee_type']


class FeeInvoice(TimeUserStamps):
    """Student Fee Invoices"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_invoices')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True)
    year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_invoices'
        ordering = ['-created_at']


class FeeInvoiceItem(TimeUserStamps):
    """Individual Fee Items in Invoice"""
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name='items')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'fee_invoice_items'


class FeePayment(TimeUserStamps):
    """Fee Payment Transactions"""
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('check', 'Cheque'),
        ('online', 'Online Transfer'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
    )
    
    payment_id = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_reference = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fee_payments'
        ordering = ['-created_at']


class FeeDiscount(TimeUserStamps):
    """Fee Discounts/Scholarships"""
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applicable_fee_types = models.ManyToManyField(FeeType)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'fee_discounts'


class StudentDiscount(TimeUserStamps):
    """Student-specific Discounts"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discounts')
    discount = models.ForeignKey(FeeDiscount, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'student_discounts'
