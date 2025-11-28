from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    FeeType, FeeStructure, FeeInvoice, FeeInvoiceItem, 
    FeePayment, FeeDiscount, StudentDiscount
)
from apps.academic.serializers import AcademicYearListingSerializer, ClassListingSerializer
from apps.users.serializers import StudentListingSerializer


# ==================== Fee Type Serializers ====================

class FeeTypeListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for fee type listings"""
    
    class Meta:
        model = FeeType
        fields = ['id', 'name', 'code', 'is_recurring']


class FeeTypeSerializer(serializers.ModelSerializer):
    """Full fee type serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    structures_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeType
        fields = [
            'id', 'name', 'code', 'description', 'is_recurring',
            'created_by', 'updated_by', 'created_at', 'updated_at', 'structures_count'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_structures_count(self, obj):
        if obj.deleted:
            return 0
        return obj.feestructure_set.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Fee type name must be at least 2 characters long")
        
        qs = FeeType.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Fee type with name '{value}' already exists")
        
        return value.strip()
    
    def validate_code(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Fee type code must be at least 2 characters long")
        
        qs = FeeType.objects.filter(code__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Fee type with code '{value}' already exists")
        
        return value.strip().upper()
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Fee type "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Fee Structure Serializers ====================

class FeeStructureListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for fee structure listings"""
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'class_name', 'fee_type_name', 'amount', 'frequency']


class FeeStructureSerializer(serializers.ModelSerializer):
    """Full fee structure serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    class_level_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    fee_type_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeStructure
        fields = [
            'id', 'class_level', 'academic_year', 'fee_type', 'amount',
            'frequency', 'due_date_day',
            'class_level_detail', 'academic_year_detail', 'fee_type_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_class_level_detail(self, obj):
        if obj.class_level and not obj.class_level.deleted:
            return ClassListingSerializer(obj.class_level).data
        return None
    
    def get_academic_year_detail(self, obj):
        if obj.academic_year and not obj.academic_year.deleted:
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def get_fee_type_detail(self, obj):
        if obj.fee_type and not obj.fee_type.deleted:
            return FeeTypeListingSerializer(obj.fee_type).data
        return None
    
    def validate_class_level(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted class")
        return value
    
    def validate_academic_year(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted academic year")
        return value
    
    def validate_fee_type(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted fee type")
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate_due_date_day(self, value):
        if value < 1 or value > 31:
            raise serializers.ValidationError("Due date day must be between 1 and 31")
        return value
    
    def validate(self, data):
        """Cross-field validation for unique together constraint"""
        class_level = data.get('class_level', getattr(self.instance, 'class_level', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        fee_type = data.get('fee_type', getattr(self.instance, 'fee_type', None))
        
        if class_level and academic_year and fee_type:
            qs = FeeStructure.objects.filter(
                class_level=class_level,
                academic_year=academic_year,
                fee_type=fee_type,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"Fee structure for '{fee_type.name}' already exists for class '{class_level.name}' in '{academic_year.name}'"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Fee structure has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Fee Invoice Item Serializers ====================

class FeeInvoiceItemListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for fee invoice item listings"""
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)
    
    class Meta:
        model = FeeInvoiceItem
        fields = ['id', 'fee_type_name', 'amount', 'description']


class FeeInvoiceItemSerializer(serializers.ModelSerializer):
    """Full fee invoice item serializer with validations"""
    fee_type_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeInvoiceItem
        fields = ['id', 'invoice', 'fee_type', 'amount', 'description', 'fee_type_detail']
        extra_kwargs = {
            'invoice': {'required': True},
            'fee_type': {'required': True}
        }
    
    def get_fee_type_detail(self, obj):
        if obj.fee_type and not obj.fee_type.deleted:
            return FeeTypeListingSerializer(obj.fee_type).data
        return None
    
    def validate_fee_type(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted fee type")
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


# ==================== Fee Invoice Serializers ====================

class FeeInvoiceListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for fee invoice listings"""
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeInvoice
        fields = ['id', 'invoice_number', 'student_name', 'total_amount', 'due_amount', 'status', 'due_date']
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class FeeInvoiceSerializer(serializers.ModelSerializer):
    """Full fee invoice serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    items = FeeInvoiceItemListingSerializer(many=True, read_only=True)
    payments_count = serializers.SerializerMethodField()
    balance_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeInvoice
        fields = [
            'id', 'invoice_number', 'student', 'academic_year', 'month', 'year',
            'total_amount', 'discount_amount', 'paid_amount', 'due_amount',
            'due_date', 'status',
            'student_detail', 'academic_year_detail', 'items', 'payments_count',
            'balance_amount', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListingSerializer(obj.student).data
        return None
    
    def get_academic_year_detail(self, obj):
        if obj.academic_year and not obj.academic_year.deleted:
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def get_payments_count(self, obj):
        if obj.deleted:
            return 0
        return obj.payments.filter(deleted=False).count()
    
    def get_balance_amount(self, obj):
        return obj.due_amount
    
    def validate_invoice_number(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Invoice number must be at least 3 characters long")
        
        qs = FeeInvoice.objects.filter(invoice_number__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Invoice number '{value}' already exists")
        
        return value.strip()
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot create invoice for a deleted student")
        return value
    
    def validate_academic_year(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted academic year")
        return value
    
    def validate_month(self, value):
        if value is not None and (value < 1 or value > 12):
            raise serializers.ValidationError("Month must be between 1 and 12")
        return value
    
    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total amount must be greater than 0")
        return value
    
    def validate_discount_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Discount amount cannot be negative")
        return value
    
    def validate_paid_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Paid amount cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        total_amount = data.get('total_amount', getattr(self.instance, 'total_amount', None))
        discount_amount = data.get('discount_amount', getattr(self.instance, 'discount_amount', 0))
        paid_amount = data.get('paid_amount', getattr(self.instance, 'paid_amount', 0))
        
        # Validate discount doesn't exceed total
        if discount_amount and total_amount and discount_amount > total_amount:
            raise serializers.ValidationError({
                'discount_amount': 'Discount cannot exceed total amount'
            })
        
        # Validate paid doesn't exceed total minus discount
        if total_amount and discount_amount is not None:
            net_amount = total_amount - discount_amount
            if paid_amount > net_amount:
                raise serializers.ValidationError({
                    'paid_amount': 'Paid amount cannot exceed net payable amount'
                })
        
        # Auto-calculate due_amount
        if total_amount is not None:
            discount = discount_amount if discount_amount else 0
            paid = paid_amount if paid_amount else 0
            data['due_amount'] = total_amount - discount - paid
        
        # Auto-update status based on payments
        if 'paid_amount' in data or 'total_amount' in data or 'discount_amount' in data:
            total = data.get('total_amount', getattr(self.instance, 'total_amount', 0))
            discount = data.get('discount_amount', getattr(self.instance, 'discount_amount', 0))
            paid = data.get('paid_amount', getattr(self.instance, 'paid_amount', 0))
            net_amount = total - discount
            
            if paid >= net_amount:
                data['status'] = 'paid'
            elif paid > 0:
                data['status'] = 'partial'
            else:
                # Check if overdue
                from datetime import date
                due_date = data.get('due_date', getattr(self.instance, 'due_date', None))
                if due_date and due_date < date.today():
                    data['status'] = 'overdue'
                else:
                    data['status'] = 'pending'
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'invoice_number': instance.invoice_number,
                'message': f'Invoice "{instance.invoice_number}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Fee Payment Serializers ====================

class FeePaymentListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for fee payment listings"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = FeePayment
        fields = ['id', 'payment_id', 'invoice_number', 'amount', 'payment_date', 'payment_method']


class FeePaymentSerializer(serializers.ModelSerializer):
    """Full fee payment serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    invoice_detail = serializers.SerializerMethodField()
    received_by_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = FeePayment
        fields = [
            'id', 'payment_id', 'invoice', 'amount', 'payment_date',
            'payment_method', 'transaction_reference', 'remarks', 'received_by',
            'invoice_detail', 'received_by_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_invoice_detail(self, obj):
        if obj.invoice and not obj.invoice.deleted:
            return FeeInvoiceListingSerializer(obj.invoice).data
        return None
    
    def get_received_by_detail(self, obj):
        if obj.received_by and not obj.received_by.deleted:
            return UserListingSerializer(obj.received_by).data
        return None
    
    def validate_payment_id(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Payment ID must be at least 3 characters long")
        
        qs = FeePayment.objects.filter(payment_id__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Payment ID '{value}' already exists")
        
        return value.strip()
    
    def validate_invoice(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot add payment to a deleted invoice")
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        invoice = data.get('invoice', getattr(self.instance, 'invoice', None))
        amount = data.get('amount', getattr(self.instance, 'amount', None))
        
        if invoice and amount:
            # Check if payment amount doesn't exceed due amount
            remaining_due = invoice.due_amount
            if self.instance:
                # If updating, add back the old payment amount
                remaining_due += self.instance.amount
            
            if amount > remaining_due:
                raise serializers.ValidationError({
                    'amount': f'Payment amount cannot exceed remaining due amount ({remaining_due})'
                })
        
        return data
    
    def create(self, validated_data):
        """Update invoice paid_amount when payment is created"""
        payment = super().create(validated_data)
        invoice = payment.invoice
        invoice.paid_amount += payment.amount
        invoice.due_amount -= payment.amount
        
        # Update status
        if invoice.due_amount <= 0:
            invoice.status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'partial'
        
        invoice.save()
        return payment
    
    def update(self, instance, validated_data):
        """Update invoice paid_amount when payment is updated"""
        old_amount = instance.amount
        payment = super().update(instance, validated_data)
        
        if 'amount' in validated_data:
            invoice = payment.invoice
            amount_difference = payment.amount - old_amount
            invoice.paid_amount += amount_difference
            invoice.due_amount -= amount_difference
            
            # Update status
            if invoice.due_amount <= 0:
                invoice.status = 'paid'
            elif invoice.paid_amount > 0:
                invoice.status = 'partial'
            else:
                invoice.status = 'pending'
            
            invoice.save()
        
        return payment
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'payment_id': instance.payment_id,
                'message': f'Payment "{instance.payment_id}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Fee Discount Serializers ====================

class FeeDiscountListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for fee discount listings"""
    
    class Meta:
        model = FeeDiscount
        fields = ['id', 'name', 'discount_type', 'value', 'is_active']


class FeeDiscountSerializer(serializers.ModelSerializer):
    """Full fee discount serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    applicable_fee_types_detail = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeDiscount
        fields = [
            'id', 'name', 'discount_type', 'value', 'applicable_fee_types',
            'description', 'is_active',
            'applicable_fee_types_detail', 'students_count',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_applicable_fee_types_detail(self, obj):
        fee_types = obj.applicable_fee_types.filter(deleted=False)
        return FeeTypeListingSerializer(fee_types, many=True).data
    
    def get_students_count(self, obj):
        if obj.deleted:
            return 0
        return obj.studentdiscount_set.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Discount name must be at least 2 characters long")
        
        qs = FeeDiscount.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Discount with name '{value}' already exists")
        
        return value.strip()
    
    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        discount_type = data.get('discount_type', getattr(self.instance, 'discount_type', None))
        value = data.get('value', getattr(self.instance, 'value', None))
        
        if discount_type == 'percentage' and value:
            if value > 100:
                raise serializers.ValidationError({
                    'value': 'Percentage discount cannot exceed 100%'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Discount "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Student Discount Serializers ====================

class StudentDiscountListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for student discount listings"""
    student_name = serializers.SerializerMethodField()
    discount_name = serializers.CharField(source='discount.name', read_only=True)
    
    class Meta:
        model = StudentDiscount
        fields = ['id', 'student_name', 'discount_name', 'start_date', 'end_date']
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class StudentDiscountSerializer(serializers.ModelSerializer):
    """Full student discount serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    discount_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    approved_by_detail = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentDiscount
        fields = [
            'id', 'student', 'discount', 'academic_year', 'start_date',
            'end_date', 'approved_by', 'remarks',
            'student_detail', 'discount_detail', 'academic_year_detail',
            'approved_by_detail', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListingSerializer(obj.student).data
        return None
    
    def get_discount_detail(self, obj):
        if obj.discount and not obj.discount.deleted:
            return FeeDiscountListingSerializer(obj.discount).data
        return None
    
    # def get_academic_year_detail(self, obj):
    #     if obj.academic_year and not obj.