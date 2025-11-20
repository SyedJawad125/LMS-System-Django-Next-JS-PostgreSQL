import re
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate

from utils.helpers import generate_token
from utils.response_messages import *
from utils.reusable_functions import combine_role_permissions, extract_permission_codes, get_first_error
from django.db import transaction
from utils.enums import *
from utils.validators import clean_and_validate_mobile
from django.utils import timezone
from .models import Parent, Student, Teacher, User, Employee, Role, Permission
from config.settings import (MAX_LOGIN_ATTEMPTS, SIMPLE_JWT, PASSWORD_MIN_LENGTH)
from django.contrib.auth.hashers import check_password
from .utils import validate_password


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=100, required=True)

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get("password", None)
        if username and password:
            user_obj = User.objects.filter(username=username, deleted=False).first()
            # user = authenticate(username=username, password=password, deleted=False)
            # if not user:
            if user_obj:
                if user_obj.activation_link_token or not user_obj.is_verified:
                    raise serializers.ValidationError(FOLLOW_ACTIVATION_EMAIL)
                if not check_password(password, user_obj.password):
                    if user_obj.login_attempts < MAX_LOGIN_ATTEMPTS:
                        user_obj.login_attempts += 1
                        user_obj.save()
                    else:
                        user_obj.is_blocked = True
                        user_obj.save()
                        raise serializers.ValidationError(ACCOUNT_BLOCKED)
                    raise serializers.ValidationError(INVALID_CREDENTIALS)
                elif user_obj.deleted:
                    raise serializers.ValidationError(INVALID_CREDENTIALS)
                elif user_obj.is_blocked:
                    raise serializers.ValidationError(ACCOUNT_BLOCKED)
                else:
                    user_obj.last_login = None
                    user_obj.login_attempts = 0
                    user_obj.save()
            else:
                raise serializers.ValidationError(INVALID_CREDENTIALS)
        else:
            raise serializers.ValidationError(USERNAME_OR_PASSWORD_MISSING)

        attrs['user'] = user_obj
        return attrs


class LoginUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'full_name', 'username', 'email', 'mobile', 'profile_image', 'role', 'type')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        tokens = self.context.get('tokens')
        data['refresh_token'] = tokens['refresh']
        data['access_token'] = tokens['access']
        expiry = SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        data['age_in_seconds'] = expiry.total_seconds() * 1000
        data['permissions'] = combine_role_permissions(instance.role)
        return data


class EmptySerializer(serializers.Serializer):
    pass


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500, required=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token', None)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            raise serializers.ValidationError(INVALID_TOKEN)
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(
        label="token",
        style={"input_type": "token"},
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        label="new_password",
        style={"input_type": "new_password"},
        trim_whitespace=True,
    )
    confirm_password = serializers.CharField(
        label="confirm_password",
        style={"input_type": "confirm_password"},
        trim_whitespace=True,
    )

    def validate(self, instance):
        if instance['new_password'] != instance['confirm_password']:
            raise serializers.ValidationError(PASSWORD_DOES_NOT_MATCH)
        elif len(instance["new_password"]) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(PasswordMustBeEightChar)
        elif not validate_password(instance["new_password"]):
            raise serializers.ValidationError(FOLLOW_PASSWORD_PATTERN)
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        email = attrs.get('username', attrs.get('email'))

        if self.instance:
            if User.objects.filter(email=email, deleted=False).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('User with this email already exists')
        else:
            if User.objects.filter(email=email, deleted=False).exists():
                raise serializers.ValidationError('User with this email already exists')
        return attrs

    def create(self, validated_data):
        instance = User.objects.create(**validated_data)
        token_string = f"{instance.id}_{instance.username}"
        token = generate_token(token_string)
        instance.activation_link_token = token
        instance.activation_link_token_created_at = timezone.now()
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'full_name', 'email', 'mobile', 'profile_image', 'role', 'deactivated')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['role'] = RoleListingSerializer(instance.role).data if instance.role else None
        return data

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ('deleted',)

    def create(self, validated_data):
        request = self.context.get('request')
        request.data['type'] = EMPLOYEE
        with transaction.atomic():
            user_instance = UserSerializer(data=request.data)
            if user_instance.is_valid():
                user_instance = user_instance.save()
            else:
                transaction.set_rollback(True)
                raise Exception(get_first_error(user_instance.errors))

            instance = Employee.objects.create(user=user_instance, **validated_data)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        data['created_by'] = instance.created_by.full_name
        data['updated_by'] = instance.updated_by.full_name if instance.updated_by else None
        user_data = UserListSerializer(instance.user).data
        del user_data['id']
        del data['user']
        data.update(user_data)
        if request.method == POST:
            data['activation_link_token'] = instance.user.activation_link_token
        return data


class RoleListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'code_name')


class PermissionListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'code_name')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

    def validate(self, attrs):
        name = attrs.get('name', None)
        code_name = attrs.get('code_name', None)

        if self.instance:
            if Role.objects.filter(name__iexact=name, deleted=False).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Role with this name already exists')
            elif Role.objects.filter(code_name__iexact=code_name, deleted=False).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Role with this code name already exists')
        else:
            if Role.objects.filter(name__iexact=name, deleted=False).exists():
                raise serializers.ValidationError('Role with this name already exists')
            elif Role.objects.filter(code_name__iexact=code_name, deleted=False).exists():
                raise serializers.ValidationError('Role with this code name already exists')
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.full_name if instance.created_by else None
        data['updated_by'] = instance.updated_by.full_name if instance.updated_by else None
        data['permissions'] = PermissionListingSerializer(instance.permissions.all(), many=True).data if data['permissions'] else []
        return data



class StudentSerializer(serializers.ModelSerializer):
    """Full student serializer with validations"""
    guardian_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        exclude = ['deleted']
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 
                            'admission_date')
    
    def get_guardian_count(self, obj):
        return obj.parents.count()
    
    def validate_admission_number(self, value):
        """Validate admission number"""
        if not value.strip():
            raise serializers.ValidationError("Admission number is required")
        
        # Check for duplicate admission numbers
        qs = Student.objects.filter(admission_number__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Student with admission number '{value}' already exists")
        
        return value.strip().upper()
    
    def validate_roll_number(self, value):
        """Validate roll number"""
        if value:
            # Check for duplicate roll numbers
            qs = Student.objects.filter(roll_number__iexact=value.strip(), deleted=False)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(f"Student with roll number '{value}' already exists")
        
        return value.strip() if value else value
    
    def validate_admission_date(self, value):
        """Validate admission date"""
        if value:
            if value > timezone.now().date():
                raise serializers.ValidationError("Admission date cannot be in the future")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Auto-generate admission number if not provided
        if not attrs.get('admission_number') and not self.instance:
            current_year = timezone.now().year
            last_student = Student.objects.filter(
                admission_date__year=current_year, 
                deleted=False
            ).order_by('-admission_number').first()
            
            if last_student and last_student.admission_number:
                try:
                    # Try to extract and increment the number
                    last_num = last_student.admission_number
                    if '-' in last_num:
                        last_id = int(last_num.split('-')[-1])
                        new_id = f"ADM-{current_year}-{last_id + 1:04d}"
                    else:
                        # If format is different, just append sequence
                        new_id = f"ADM-{current_year}-0001"
                except (ValueError, IndexError):
                    new_id = f"ADM-{current_year}-0001"
            else:
                new_id = f"ADM-{current_year}-0001"
            
            attrs['admission_number'] = new_id
        
        # Set admission date to current date if not provided
        if not attrs.get('admission_date') and not self.instance:
            attrs['admission_date'] = timezone.now().date()
        
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
        data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
        # Add user data if user exists
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'full_name': instance.user.full_name,
                'email': instance.user.email,
                'mobile': instance.user.mobile
            }
        
        return data


class StudentListingSerializer(serializers.ModelSerializer):
    """Simplified serializer for student listings"""
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'roll_number', 'full_name', 'email', 'mobile', 'gender', 'status']
    
    def get_full_name(self, obj):
        """Get full name from user if exists, otherwise from student data"""
        if obj.user and obj.user.full_name:
            return obj.user.full_name
        # If no user linked, you might want to store name in Student model
        # or return admission number as identifier
        return f"Student {obj.admission_number}"
    
    def get_email(self, obj):
        """Get email from user if exists"""
        return obj.user.email if obj.user else None
    
    def get_mobile(self, obj):
        """Get mobile from user if exists"""
        return obj.user.mobile if obj.user else None


class TeacherSerializer(serializers.ModelSerializer):
    """Full teacher serializer with validations"""
    
    class Meta:
        model = Teacher
        exclude = ['deleted']
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def validate_employee_id(self, value):
        """Validate employee ID"""
        if not value.strip():
            raise serializers.ValidationError("Employee ID is required")
        
        # Check for duplicate employee IDs
        qs = Teacher.objects.filter(employee_id__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Teacher with employee ID '{value}' already exists")
        
        return value.strip().upper()
    
    def validate_qualification(self, value):
        """Validate qualification"""
        if not value.strip():
            raise serializers.ValidationError("Qualification is required")
        
        if len(value) > 255:
            raise serializers.ValidationError("Qualification cannot exceed 255 characters")
        return value.strip()
    
    def validate_specialization(self, value):
        """Validate specialization"""
        if value and len(value) > 255:
            raise serializers.ValidationError("Specialization cannot exceed 255 characters")
        return value.strip() if value else value
    
    def validate_experience_years(self, value):
        """Validate experience years"""
        if value and value < 0:
            raise serializers.ValidationError("Experience cannot be negative")
        
        if value and value > 50:
            raise serializers.ValidationError("Experience years seem too high")
        return value
    
    def validate_joining_date(self, value):
        """Validate joining date"""
        if value:
            if value > timezone.now().date():
                raise serializers.ValidationError("Joining date cannot be in the future")
        return value
    
    def validate_salary(self, value):
        """Validate salary"""
        if value and value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Auto-generate employee ID if not provided
        if not attrs.get('employee_id') and not self.instance:
            current_year = timezone.now().year
            last_teacher = Teacher.objects.filter(
                joining_date__year=current_year, 
                deleted=False
            ).order_by('-employee_id').first()
            
            if last_teacher and last_teacher.employee_id:
                try:
                    last_id = int(last_teacher.employee_id.split('-')[-1])
                    new_id = f"EMP-{current_year}-{last_id + 1:04d}"
                except (ValueError, IndexError):
                    new_id = f"EMP-{current_year}-0001"
            else:
                new_id = f"EMP-{current_year}-0001"
            
            attrs['employee_id'] = new_id
        
        # Set joining date to current date if not provided
        if not attrs.get('joining_date') and not self.instance:
            attrs['joining_date'] = timezone.now().date()
        
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
        data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
        # Add user data if user exists
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'full_name': instance.user.full_name,
                'email': instance.user.email,
                'mobile': instance.user.mobile
            }
        
        return data

class ParentSerializer(serializers.ModelSerializer):
    """Full parent serializer with validations"""
    children_list = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Parent
        exclude = ['deleted']
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_children_list(self, obj):
        return StudentListingSerializer(obj.students.filter(deleted=False), many=True).data
    
    def get_children_count(self, obj):
        return obj.students.filter(deleted=False).count()
    
    def validate_relation(self, value):
        """Validate relation"""
        if not value.strip():
            raise serializers.ValidationError("Relation is required")
        
        valid_relations = ['father', 'mother', 'guardian']
        if value not in valid_relations:
            raise serializers.ValidationError(f"Relation must be one of: {', '.join(valid_relations)}")
        
        return value.strip()
    
    def validate_occupation(self, value):
        """Validate occupation"""
        if value and len(value) > 100:
            raise serializers.ValidationError("Occupation cannot exceed 100 characters")
        return value.strip() if value else value
    
    def validate_annual_income(self, value):
        """Validate annual income"""
        if value and value < 0:
            raise serializers.ValidationError("Annual income cannot be negative")
        return value
    
    def validate_office_address(self, value):
        """Validate office address"""
        if value and len(value) > 500:
            raise serializers.ValidationError("Office address cannot exceed 500 characters")
        return value.strip() if value else value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Validate that students are provided
        students = attrs.get('students', [])
        if not students and not self.instance:
            raise serializers.ValidationError({
                "students": "At least one student must be associated with the parent"
            })
        
        # Validate maximum number of students per parent
        if students and len(students) > 10:
            raise serializers.ValidationError({
                "students": "A parent cannot be associated with more than 10 students"
            })
        
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
        data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
        # Add user data if user exists
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'full_name': instance.user.full_name,
                'email': instance.user.email,
                'mobile': instance.user.mobile
            }
        
        return data