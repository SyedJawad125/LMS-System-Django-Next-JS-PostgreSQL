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
    
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
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
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Ensure due_amount is calculated before saving
        if not self.due_amount and self.total_amount is not None:
            self.due_amount = self.total_amount - (self.discount_amount or 0) - (self.paid_amount or 0)
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """
        Generate clean sequential invoice number per academic year
        Format: INV-2024-25-0001, INV-2024-25-0002, etc.
        """
        academic_year_code = self.academic_year.code
        
        # Get the last invoice number for this academic year
        last_invoice = FeeInvoice.objects.filter(
            academic_year=self.academic_year,
            invoice_number__startswith=f"INV-{academic_year_code}-"
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            try:
                # Extract the sequential number from last invoice
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"INV-{academic_year_code}-{new_number:04d}"
    
    def update_status(self):
        """Update invoice status based on current amounts and due date"""
        from datetime import date
        
        net_amount = self.total_amount - (self.discount_amount or 0)
        
        if self.paid_amount >= net_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.due_date and self.due_date < date.today():
            self.status = 'overdue'
        else:
            self.status = 'pending'
        
        self.save()
        
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
    
    payment_id = models.CharField(max_length=50, unique=True, blank=True)
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
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        super().save(*args, **kwargs)
    
    def generate_payment_id(self):
        """
        Generate sequential payment ID per academic year
        Format: PAY-2024-25-0001, PAY-2024-25-0002, etc.
        """
        # Get academic year code from the invoice
        academic_year_code = self.invoice.academic_year.code
        
        # Get the last payment ID for this academic year
        last_payment = FeePayment.objects.filter(
            invoice__academic_year=self.invoice.academic_year,
            payment_id__startswith=f"PAY-{academic_year_code}-"
        ).order_by('-payment_id').first()
        
        if last_payment:
            try:
                # Extract the sequential number from last payment
                last_number = int(last_payment.payment_id.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"PAY-{academic_year_code}-{new_number:04d}"

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
