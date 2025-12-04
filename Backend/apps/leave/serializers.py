from datetime import date
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q

from utils.enums import *
from .models import (
    LeaveType, LeaveApplication, LeaveBalance, 
    LeaveConfiguration, LeaveApprovalWorkflow, LeaveHistory
)


# ==================== Leave Type Serializers ====================

class LeaveTypeListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave type listings"""
    
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'code', 'max_days_per_year', 'is_active']


class LeaveTypeSerializer(serializers.ModelSerializer):
    """Full leave type serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveType
        fields = [
            'id', 'name', 'code', 'max_days_per_year', 'requires_approval',
            'description', 'is_active', 'applications_count',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('code', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
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
    
    def get_applications_count(self, obj):
        """Get count of non-deleted applications"""
        if obj.deleted:
            return 0
        return obj.applications.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Leave type name must be at least 2 characters long")
        
        qs = LeaveType.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Leave type with name '{value}' already exists")
        
        return value.strip()
    
    def validate_max_days_per_year(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max days per year must be greater than 0")
        if value > 365:
            raise serializers.ValidationError("Max days per year cannot exceed 365")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Leave type "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Leave Application Serializer ====================

class LeaveApplicationListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave application listings"""
    applicant_name = serializers.CharField(read_only=True)
    applicant_type = serializers.CharField(read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'application_number', 'applicant_name', 'applicant_type',
            'leave_type_name', 'start_date', 'end_date', 'total_days', 'status'
        ]


class LeaveApplicationSerializer(serializers.ModelSerializer):
    """Full leave application serializer with validations - Version 2"""
    
    # User tracking fields
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    
    # Related details
    leave_type_detail = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    
    # Model property fields (all @property from model)
    applicant_name = serializers.CharField(read_only=True)
    applicant_type = serializers.CharField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    is_rejected = serializers.BooleanField(read_only=True)
    is_cancelled = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    can_be_edited = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = [
            # Basic fields
            'id', 'application_number', 'teacher', 'student', 'leave_type',
            'start_date', 'end_date', 'total_days', 'reason', 'attachment',
            'status', 'applied_at', 'reviewed_by', 'reviewed_at', 'remarks',
            'emergency_contact', 'emergency_phone', 'address_during_leave',
            
            # Related details
            'leave_type_detail', 'reviewed_by_name',
            
            # Model properties (from @property decorators)
            'applicant_name', 'applicant_type', 
            'is_pending', 'is_approved', 'is_rejected', 'is_cancelled', 
            'can_be_cancelled', 'can_be_edited',
            
            # Audit fields
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            # Auto-generated by backend
            'application_number',   # Generated in model save()
            'total_days',          # Calculated in model save()
            
            # Auto-set timestamps
            'applied_at',          # auto_now_add=True
            'reviewed_at',         # Set in model save() on status change
            
            # Audit timestamps
            'created_at',          # From TimeUserStamps
            'updated_at',          # From TimeUserStamps
            'created_by',          # From TimeUserStamps
            'updated_by',          # From TimeUserStamps
        )
    
    # ==================== SerializerMethodField Methods ====================
    
    def get_created_by(self, obj):
        """Get created by user's name"""
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        """Get updated by user's name"""
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_leave_type_detail(self, obj):
        """Get detailed leave type information"""
        if obj.leave_type and not obj.leave_type.deleted:
            return {
                'id': obj.leave_type.id,
                'name': obj.leave_type.name,
                'code': obj.leave_type.code,
                'max_days_per_year': obj.leave_type.max_days_per_year,
                'requires_approval': obj.leave_type.requires_approval,
                'is_active': obj.leave_type.is_active
            }
        return None
    
    def get_reviewed_by_name(self, obj):
        """Get reviewer's name"""
        if obj.reviewed_by and not obj.reviewed_by.deleted:
            if hasattr(obj.reviewed_by, 'user') and obj.reviewed_by.user:
                full_name = obj.reviewed_by.user.get_full_name()
                return full_name.strip() if full_name and full_name.strip() else obj.reviewed_by.user.username
            return str(obj.reviewed_by)
        return None
    
    # ==================== Field-level Validations ====================
    
    def validate_teacher(self, value):
        """Validate teacher is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_student(self, value):
        """Validate student is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted student")
        return value
    
    def validate_leave_type(self, value):
        """Validate leave type is active and not deleted"""
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted leave type")
        if not value.is_active:
            raise serializers.ValidationError("This leave type is not currently active")
        return value
    
    def validate_start_date(self, value):
        """Validate start date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError("Start date cannot be in the past")
        return value
    
    def validate_end_date(self, value):
        """Validate end date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError("End date cannot be in the past")
        return value
    
    def validate_emergency_phone(self, value):
        """Validate emergency phone number format"""
        if value:
            # Remove common separators for validation
            phone = value.replace(' ', '').replace('-', '').replace('+', '').replace('(', '').replace(')', '')
            if not phone.isdigit() or len(phone) < 10:
                raise serializers.ValidationError(
                    "Emergency phone must be a valid phone number (at least 10 digits)"
                )
        return value
    
    def validate_attachment(self, value):
        """Validate attachment file size and type"""
        if value:
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB in bytes
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"Attachment size cannot exceed 5MB. Current size: {value.size / (1024 * 1024):.2f}MB"
                )
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Invalid file type '{ext}'. Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return value
    
    # ==================== Object-level Validation ====================
    
    def validate(self, data):
        """
        Cross-field validation for leave application.
        Handles complex business logic validations.
        """
        # Get values from data or instance (for updates)
        teacher = data.get('teacher', getattr(self.instance, 'teacher', None))
        student = data.get('student', getattr(self.instance, 'student', None))
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        leave_type = data.get('leave_type', getattr(self.instance, 'leave_type', None))
        
        # 1. Validate teacher/student exclusivity (model clean() also checks this)
        if not teacher and not student:
            raise serializers.ValidationError({
                'teacher': 'Either teacher or student must be selected',
                'student': 'Either teacher or student must be selected'
            })
        
        if teacher and student:
            raise serializers.ValidationError({
                'teacher': 'Cannot select both teacher and student',
                'student': 'Cannot select both teacher and student'
            })
        
        # 2. Validate date range
        if start_date and end_date:
            # Check if end date is before start date
            if start_date > end_date:
                raise serializers.ValidationError({
                    'end_date': 'End date cannot be before start date'
                })
            
            # Calculate total days
            total_days = (end_date - start_date).days + 1
            
            # 3. Check against leave type max days per year
            if leave_type and total_days > leave_type.max_days_per_year:
                raise serializers.ValidationError({
                    'end_date': f'Total days ({total_days}) exceeds maximum allowed for this leave type ({leave_type.max_days_per_year} days per year)'
                })
            
            # 4. Check for overlapping leave applications
            # Only check on create or when dates are being changed
            should_check_overlap = (
                not self.instance or  # Creating new
                self.instance.start_date != start_date or  # Start date changed
                self.instance.end_date != end_date  # End date changed
            )
            
            if should_check_overlap:
                applicant = teacher or student
                applicant_field = 'teacher' if teacher else 'student'
                
                # Query for overlapping applications
                overlapping = LeaveApplication.objects.filter(
                    **{applicant_field: applicant},
                    deleted=False,
                    status__in=[PENDING, APPROVED]  # Only check pending/approved applications
                ).filter(
                    Q(start_date__lte=end_date, end_date__gte=start_date)  # Date range overlap
                )
                
                # Exclude current instance when updating
                if self.instance:
                    overlapping = overlapping.exclude(id=self.instance.id)
                
                # Raise error if overlap found
                if overlapping.exists():
                    overlap = overlapping.first()
                    raise serializers.ValidationError({
                        'start_date': f'Leave dates overlap with existing application {overlap.application_number} ({overlap.start_date} to {overlap.end_date})',
                        'end_date': f'Leave dates overlap with existing application {overlap.application_number} ({overlap.start_date} to {overlap.end_date})'
                    })
        
        return data
    
    # ==================== Custom Representation ====================
    
    def to_representation(self, instance):
        """
        Customize the output representation.
        Format datetime fields and handle soft-deleted instances.
        """
        # Handle soft-deleted instances
        if instance.deleted:
            return {
                'id': instance.id,
                'application_number': instance.application_number,
                'message': f'Leave application "{instance.application_number}" has been deleted successfully'
            }
        
        # Get standard representation
        data = super().to_representation(instance)
        
        # Format datetime fields to be more readable
        datetime_fields = ['created_at', 'updated_at', 'applied_at', 'reviewed_at']
        for field in datetime_fields:
            if data.get(field) and isinstance(data[field], str):
                # Remove 'T' and microseconds: "2024-12-04T10:30:45.123456" -> "2024-12-04 10:30:45"
                data[field] = data[field].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Leave History Serializers ====================

class LeaveHistoryListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave history listings"""
    application_number = serializers.CharField(source='leave_application.application_number', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by_name', read_only=True)
    action_display = serializers.CharField(source='action_display', read_only=True)
    
    class Meta:
        model = LeaveHistory
        fields = [
            'id', 'application_number', 'action', 'action_display',
            'changed_by_name', 'created_at'
        ]


class LeaveHistorySerializer(serializers.ModelSerializer):
    """Full leave history serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    leave_application_detail = serializers.SerializerMethodField()
    changed_by_detail = serializers.SerializerMethodField()
    changed_by_name = serializers.CharField(source='changed_by_name', read_only=True)
    action_display = serializers.CharField(source='action_display', read_only=True)
    
    class Meta:
        model = LeaveHistory
        fields = [
            'id', 'leave_application', 'action', 'changed_by', 'previous_status',
            'new_status', 'changes', 'ip_address', 'user_agent', 'remarks',
            'leave_application_detail', 'changed_by_detail', 'changed_by_name',
            'action_display',
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
    
    def get_leave_application_detail(self, obj):
        if obj.leave_application and not obj.leave_application.deleted:
            return LeaveApplicationListSerializer(obj.leave_application).data
        return None
    
    def get_changed_by_detail(self, obj):
        if obj.changed_by and not obj.changed_by.deleted:
            return {
                'id': obj.changed_by.id,
                'username': obj.changed_by.username,
                'full_name': obj.changed_by_name
            }
        return None
    
    def validate_leave_application(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted leave application")
        return value
    
    def validate_changed_by(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted user")
        return value
    
    def validate_changes(self, value):
        """Ensure changes is a valid dict/JSON"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Changes must be a valid JSON object")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'leave_application': instance.leave_application_id,
                'action': instance.action,
                'message': f'Leave history record has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Leave Application Serializers ====================

class LeaveApplicationListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave application listings"""
    applicant_name = serializers.CharField(read_only=True)  # Remove source
    applicant_type = serializers.CharField(read_only=True)  # Remove source
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'application_number', 'applicant_name', 'applicant_type',
            'leave_type_name', 'start_date', 'end_date', 'total_days', 'status'
        ]


class LeaveApplicationSerializer(serializers.ModelSerializer):
    """Full leave application serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    leave_type_detail = serializers.SerializerMethodField()
    applicant_name = serializers.CharField(read_only=True)  # Remove source
    applicant_type = serializers.CharField(read_only=True)  # Remove source
    is_pending = serializers.BooleanField(read_only=True)  # Remove source
    is_approved = serializers.BooleanField(read_only=True)  # Remove source
    can_be_cancelled = serializers.BooleanField(read_only=True)  # Remove source
    reviewed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'application_number', 'teacher', 'student', 'leave_type',
            'start_date', 'end_date', 'total_days', 'reason', 'attachment',
            'status', 'applied_at', 'reviewed_by', 'reviewed_at', 'remarks',
            'emergency_contact', 'emergency_phone', 'address_during_leave',
            'leave_type_detail', 'applicant_name', 'applicant_type',
            'is_pending', 'is_approved', 'can_be_cancelled', 'reviewed_by_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'application_number', 'total_days', 'applied_at', 'reviewed_at',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        )
    
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
    
    def get_leave_type_detail(self, obj):
        if obj.leave_type and not obj.leave_type.deleted:
            return LeaveTypeListSerializer(obj.leave_type).data
        return None
    
    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            full_name = obj.reviewed_by.get_full_name() if hasattr(obj.reviewed_by, 'get_full_name') else None
            return full_name.strip() if full_name and full_name.strip() else str(obj.reviewed_by)
        return None
    
    def validate_teacher(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_student(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted student")
        return value
    
    def validate_leave_type(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted leave type")
        if not value.is_active:
            raise serializers.ValidationError("This leave type is not active")
        return value
    
    def validate_start_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Start date cannot be in the past")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        teacher = data.get('teacher', getattr(self.instance, 'teacher', None))
        student = data.get('student', getattr(self.instance, 'student', None))
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        
        # Validate either teacher or student, not both
        if not teacher and not student:
            raise serializers.ValidationError({
                'teacher': 'Either teacher or student must be selected',
                'student': 'Either teacher or student must be selected'
            })
        
        if teacher and student:
            raise serializers.ValidationError({
                'teacher': 'Cannot select both teacher and student',
                'student': 'Cannot select both teacher and student'
            })
        
        # Validate date range
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError({
                    'end_date': 'End date cannot be before start date'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'application_number': instance.application_number,
                'message': f'Leave application "{instance.application_number}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('applied_at'), str):
            data['applied_at'] = data['applied_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('reviewed_at'), str):
            data['reviewed_at'] = data['reviewed_at'].replace('T', ' ').split('.')[0]
        
        return data

# ==================== Leave Balance Serializers ====================

class LeaveBalanceListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave balance listings"""
    applicant_name = serializers.SerializerMethodField()
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'applicant_name', 'leave_type_name', 'academic_year',
            'total_allocated', 'used', 'remaining'
        ]
    
    def get_applicant_name(self, obj):
        if obj.applicant:
            return obj.applicant.get_full_name() if hasattr(obj.applicant, 'get_full_name') else str(obj.applicant)
        return "Unknown"


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Full leave balance serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    leave_type_detail = serializers.SerializerMethodField()
    applicant_name = serializers.SerializerMethodField()
    applicant_type = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'teacher', 'student', 'leave_type', 'academic_year',
            'total_allocated', 'used', 'remaining', 'carried_over',
            'leave_type_detail', 'applicant_name', 'applicant_type',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('remaining', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
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
    
    def get_leave_type_detail(self, obj):
        if obj.leave_type and not obj.leave_type.deleted:
            return LeaveTypeListSerializer(obj.leave_type).data
        return None
    
    def get_applicant_name(self, obj):
        if obj.applicant:
            return obj.applicant.get_full_name() if hasattr(obj.applicant, 'get_full_name') else str(obj.applicant)
        return "Unknown"
    
    def get_applicant_type(self, obj):
        if obj.teacher:
            return 'teacher'
        elif obj.student:
            return 'student'
        return None
    
    def validate_teacher(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_student(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted student")
        return value
    
    def validate_leave_type(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted leave type")
        return value
    
    def validate_total_allocated(self, value):
        if value < 0:
            raise serializers.ValidationError("Total allocated cannot be negative")
        return value
    
    def validate_used(self, value):
        if value < 0:
            raise serializers.ValidationError("Used days cannot be negative")
        return value
    
    def validate_carried_over(self, value):
        if value < 0:
            raise serializers.ValidationError("Carried over days cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        teacher = data.get('teacher', getattr(self.instance, 'teacher', None))
        student = data.get('student', getattr(self.instance, 'student', None))
        leave_type = data.get('leave_type', getattr(self.instance, 'leave_type', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        
        # Validate either teacher or student, not both
        if not teacher and not student:
            raise serializers.ValidationError({
                'teacher': 'Either teacher or student must be selected',
                'student': 'Either teacher or student must be selected'
            })
        
        if teacher and student:
            raise serializers.ValidationError({
                'teacher': 'Cannot select both teacher and student',
                'student': 'Cannot select both teacher and student'
            })
        
        # Check unique together constraint
        if teacher and leave_type and academic_year:
            qs = LeaveBalance.objects.filter(
                teacher=teacher,
                leave_type=leave_type,
                academic_year=academic_year,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"Leave balance already exists for this teacher and leave type in academic year {academic_year}"
                )
        
        if student and leave_type and academic_year:
            qs = LeaveBalance.objects.filter(
                student=student,
                leave_type=leave_type,
                academic_year=academic_year,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"Leave balance already exists for this student and leave type in academic year {academic_year}"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Leave balance has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Leave Configuration Serializers ====================

class LeaveConfigurationListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave configuration listings"""
    
    class Meta:
        model = LeaveConfiguration
        fields = ['id', 'academic_year', 'is_active']


class LeaveConfigurationSerializer(serializers.ModelSerializer):
    """Full leave configuration serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveConfiguration
        fields = [
            'id', 'academic_year', 'max_consecutive_days', 'advance_notice_days',
            'max_advance_days', 'require_multilevel_approval', 'auto_approve_short_leaves',
            'auto_approve_max_days', 'allow_carry_over', 'max_carry_over_days',
            'carry_over_validity_months', 'notify_applicant_on_status_change',
            'notify_reviewer_on_new_application', 'is_active',
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
    
    def validate_academic_year(self, value):
        qs = LeaveConfiguration.objects.filter(academic_year=value, deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(
                f"Leave configuration for academic year {value} already exists"
            )
        
        return value
    
    def validate_max_consecutive_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max consecutive days must be greater than 0")
        return value
    
    def validate_advance_notice_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Advance notice days cannot be negative")
        return value
    
    def validate_max_advance_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max advance days must be greater than 0")
        return value
    
    def validate_auto_approve_max_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Auto approve max days cannot be negative")
        return value
    
    def validate_max_carry_over_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Max carry over days cannot be negative")
        return value
    
    def validate_carry_over_validity_months(self, value):
        if value < 0:
            raise serializers.ValidationError("Carry over validity months cannot be negative")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'academic_year': instance.academic_year,
                'message': f'Leave configuration for academic year {instance.academic_year} has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data
    


from rest_framework import serializers
from .models import LeaveApprovalWorkflow, LeaveHistory, LeaveApplication


# ==================== Leave Approval Workflow Serializers ====================

class LeaveApprovalWorkflowListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave approval workflow listings"""
    application_number = serializers.CharField(source='leave_application.application_number', read_only=True)
    approver_name = serializers.CharField(read_only=True)
    level_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'id', 'application_number', 'approval_level', 'level_name',
            'approver_name', 'status', 'is_current_level', 'is_overdue'
        ]


class LeaveApprovalWorkflowSerializer(serializers.ModelSerializer):
    """Full leave approval workflow serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    leave_application_detail = serializers.SerializerMethodField()
    approver_detail = serializers.SerializerMethodField()
    approver_name = serializers.CharField(read_only=True)
    level_name = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'id', 'leave_application', 'approval_level', 'approver', 'status',
            'comments', 'approved_at', 'deadline', 'is_current_level',
            'leave_application_detail', 'approver_detail', 'approver_name',
            'level_name', 'is_overdue',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('approved_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
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
    
    def get_leave_application_detail(self, obj):
        if obj.leave_application and not obj.leave_application.deleted:
            return {
                'id': obj.leave_application.id,
                'application_number': obj.leave_application.application_number,
                'applicant_name': obj.leave_application.applicant_name,
                'leave_type': obj.leave_application.leave_type.name if obj.leave_application.leave_type else None,
                'start_date': obj.leave_application.start_date,
                'end_date': obj.leave_application.end_date,
                'total_days': obj.leave_application.total_days,
                'status': obj.leave_application.status
            }
        return None
    
    def get_approver_detail(self, obj):
        if obj.approver and not obj.approver.deleted:
            return {
                'id': obj.approver.id,
                'name': obj.approver_name,
                'email': obj.approver.user.email if hasattr(obj.approver, 'user') and obj.approver.user else None
            }
        return None
    
    def validate_leave_application(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted leave application")
        return value
    
    def validate_approver(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_approval_level(self, value):
        if value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("Approval level must be between 1 and 4")
        return value
    
    def validate_status(self, value):
        valid_statuses = [PENDING, APPROVED, REJECTED, CANCELLED]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        leave_application = data.get('leave_application', getattr(self.instance, 'leave_application', None))
        approval_level = data.get('approval_level', getattr(self.instance, 'approval_level', None))
        
        # Check unique together constraint
        if leave_application and approval_level:
            qs = LeaveApprovalWorkflow.objects.filter(
                leave_application=leave_application,
                approval_level=approval_level,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"Approval workflow for level {approval_level} already exists for this leave application"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'leave_application': instance.leave_application_id,
                'approval_level': instance.approval_level,
                'message': f'Approval workflow for level {instance.approval_level} has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('approved_at'), str) and data.get('approved_at'):
            data['approved_at'] = data['approved_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('deadline'), str) and data.get('deadline'):
            data['deadline'] = data['deadline'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Leave History Serializers ====================

class LeaveHistoryListSerializer(serializers.ModelSerializer):
    """Minimal serializer for leave history listings"""
    application_number = serializers.CharField(source='leave_application.application_number', read_only=True)
    changed_by_name = serializers.CharField(read_only=True)
    action_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = LeaveHistory
        fields = [
            'id', 'application_number', 'action', 'action_display',
            'changed_by_name', 'new_status', 'created_at'
        ]


class LeaveHistorySerializer(serializers.ModelSerializer):
    """Full leave history serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    leave_application_detail = serializers.SerializerMethodField()
    changed_by_detail = serializers.SerializerMethodField()
    changed_by_name = serializers.CharField(read_only=True)
    action_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = LeaveHistory
        fields = [
            'id', 'leave_application', 'action', 'changed_by', 'previous_status',
            'new_status', 'changes', 'ip_address', 'user_agent', 'remarks',
            'leave_application_detail', 'changed_by_detail', 'changed_by_name',
            'action_display',
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
    
    def get_leave_application_detail(self, obj):
        if obj.leave_application and not obj.leave_application.deleted:
            return {
                'id': obj.leave_application.id,
                'application_number': obj.leave_application.application_number,
                'applicant_name': obj.leave_application.applicant_name,
                'status': obj.leave_application.status
            }
        return None
    
    def get_changed_by_detail(self, obj):
        if obj.changed_by and not obj.changed_by.deleted:
            return {
                'id': obj.changed_by.id,
                'username': obj.changed_by.username,
                'full_name': obj.changed_by_name,
                'email': obj.changed_by.email if hasattr(obj.changed_by, 'email') else None
            }
        return None
    
    def validate_leave_application(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted leave application")
        return value
    
    def validate_changed_by(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted user")
        return value
    
    def validate_action(self, value):
        valid_actions = ['created', 'submitted', 'approved', 'rejected', 'cancelled', 
                        'modified', 'forwarded', 'withdrawn']
        if value not in valid_actions:
            raise serializers.ValidationError(f"Action must be one of: {', '.join(valid_actions)}")
        return value
    
    def validate_changes(self, value):
        """Ensure changes is a valid dict/JSON"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Changes must be a valid JSON object")
        return value
    
    def validate_ip_address(self, value):
        """Validate IP address format"""
        if value:
            import ipaddress
            try:
                ipaddress.ip_address(value)
            except ValueError:
                raise serializers.ValidationError("Invalid IP address format")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'leave_application': instance.leave_application_id,
                'action': instance.action,
                'message': 'Leave history record has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Approval Action Serializers ====================

class ApprovalActionSerializer(serializers.Serializer):
    """Serializer for approval/rejection actions"""
    status = serializers.ChoiceField(choices=['approved', 'rejected'], required=True)
    comments = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be either 'approved' or 'rejected'")
        return value


class BulkApprovalActionSerializer(serializers.Serializer):
    """Serializer for bulk approval/rejection actions"""
    workflow_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    status = serializers.ChoiceField(choices=['approved', 'rejected'], required=True)
    comments = serializers.CharField(required=False, allow_blank=True)
    
    def validate_workflow_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one workflow ID is required")
        
        # Check if all workflow IDs exist
        existing_count = LeaveApprovalWorkflow.objects.filter(
            id__in=value,
            deleted=False
        ).count()
        
        if existing_count != len(value):
            raise serializers.ValidationError("Some workflow IDs are invalid or deleted")
        
        return value