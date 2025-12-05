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

# class EmployeeSerializer(serializers.ModelSerializer):
#     # Add these fields to accept user data
#     username = serializers.CharField(write_only=True, required=True)
#     first_name = serializers.CharField(write_only=True, required=True)
#     last_name = serializers.CharField(write_only=True, required=True)
#     password = serializers.CharField(write_only=True, required=True)
    
#     class Meta:
#         model = Employee
#         exclude = ('deleted',)
    
#     def create(self, validated_data):
#         request = self.context.get('request')
        
#         # Extract user data from validated_data
#         user_data = {
#             'username': validated_data.pop('username'),
#             'first_name': validated_data.pop('first_name'),
#             'last_name': validated_data.pop('last_name'),
#             'password': validated_data.pop('password'),
#             'type': EMPLOYEE  # Add employee type
#         }
        
#         # Add optional user fields if present
#         optional_fields = ['email', 'mobile', 'address']
#         for field in optional_fields:
#             if field in validated_data:
#                 user_data[field] = validated_data.pop(field)
        
#         with transaction.atomic():
#             # Create User first
#             user_serializer = UserSerializer(data=user_data)
#             if user_serializer.is_valid():
#                 user_instance = user_serializer.save()
#             else:
#                 raise serializers.ValidationError(user_serializer.errors)
            
#             # Create Employee
#             instance = Employee.objects.create(
#                 user=user_instance, 
#                 **validated_data
#             )
        
#         return instance




class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    Expects user ID in the payload.
    
    Payload example:
    {
        "user": 123,
        "status": "INVITED"
    }
    """
    
    # Read-only fields to display user info in response
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    address = serializers.CharField(source='user.address', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    activation_link_token = serializers.CharField(source='user.activation_link_token', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('employee_id', 'created_at', 'updated_at', 'deleted')
    
    def validate_user(self, value):
        """Validate that user exists and is of type EMPLOYEE"""
        if not value:
            raise serializers.ValidationError("User is required.")
        
        # Check if user already has an employee record
        if Employee.objects.filter(user=value, deleted=False).exists():
            raise serializers.ValidationError("This user already has an employee record.")
        
        # Optional: Check if user type is EMPLOYEE
        # if value.type != 'EMPLOYEE':
        #     raise serializers.ValidationError("User must be of type EMPLOYEE.")
        
        return value
    
    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)
        
        # Add user details to response
        if instance.user:
            representation['full_name'] = instance.user.full_name
            representation['email'] = instance.user.email
            representation['username'] = instance.user.username
            representation['mobile'] = instance.user.mobile
            representation['address'] = instance.user.address
            representation['is_active'] = instance.user.is_active
            representation['is_verified'] = instance.user.is_verified
            representation['activation_link_token'] = instance.user.activation_link_token
            
            if instance.user.role:
                representation['role'] = {
                    'id': instance.user.role.id,
                    'name': instance.user.role.name,
                    'code_name': instance.user.role.code_name
                }
        
        return representation
    
    def create(self, validated_data):
        request = self.context.get('request')
        
        # Set created_by and updated_by
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        # Create Employee with user_id
        instance = Employee.objects.create(**validated_data)
        
        return instance
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        
        # Don't allow changing the user relationship
        if 'user' in validated_data:
            raise serializers.ValidationError("Cannot change the user for an existing employee.")
        
        # Set updated_by
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        # Update employee fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        
        return instance


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


# Add this to your serializers.py file

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        trim_whitespace=True,
    )
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'mobile', 
            'password', 'confirm_password', 'type'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'type': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value, deleted=False).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value.lower()

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError(PASSWORD_DOES_NOT_MATCH)
        if len(password) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(PasswordMustBeEightChar)
        if not validate_password(password):
            raise serializers.ValidationError(FOLLOW_PASSWORD_PATTERN)
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        email = validated_data.get('email')
        user_type = validated_data.pop('type', CUSTOMER)
        
        user = User.objects.create(
            username=email,
            email=email,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            mobile=validated_data.get('mobile'),
            type=user_type,
            is_active=False,
            is_verified=False,
        )
        user.set_password(validated_data.get('password'))
        
        # Generate activation token
        token_string = f"{user.id}_{user.username}"
        token = generate_token(token_string)
        user.activation_link_token = token
        user.activation_link_token_created_at = timezone.now()
        user.save()
        
        return user

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'full_name': instance.full_name,
            'email': instance.email,
            'mobile': instance.mobile,
            'type': instance.type,
            'activation_link_token': instance.activation_link_token,
        }

# class StudentSerializer(serializers.ModelSerializer):
#     """Full student serializer with validations"""
#     guardian_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Student
#         exclude = ['deleted']
#         read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 
#                             'admission_date')
    
#     def get_guardian_count(self, obj):
#         return obj.parents.count()
    
#     def validate_admission_number(self, value):
#         """Validate admission number"""
#         if not value.strip():
#             raise serializers.ValidationError("Admission number is required")
        
#         # Check for duplicate admission numbers
#         qs = Student.objects.filter(admission_number__iexact=value.strip(), deleted=False)
#         if self.instance:
#             qs = qs.exclude(id=self.instance.id)
        
#         if qs.exists():
#             raise serializers.ValidationError(f"Student with admission number '{value}' already exists")
        
#         return value.strip().upper()
    
#     def validate_roll_number(self, value):
#         """Validate roll number"""
#         if value:
#             # Check for duplicate roll numbers
#             qs = Student.objects.filter(roll_number__iexact=value.strip(), deleted=False)
#             if self.instance:
#                 qs = qs.exclude(id=self.instance.id)
            
#             if qs.exists():
#                 raise serializers.ValidationError(f"Student with roll number '{value}' already exists")
        
#         return value.strip() if value else value
    
#     def validate_admission_date(self, value):
#         """Validate admission date"""
#         if value:
#             if value > timezone.now().date():
#                 raise serializers.ValidationError("Admission date cannot be in the future")
#         return value
    
#     def validate(self, attrs):
#         """Cross-field validation"""
#         # Auto-generate admission number if not provided
#         if not attrs.get('admission_number') and not self.instance:
#             current_year = timezone.now().year
#             last_student = Student.objects.filter(
#                 admission_date__year=current_year, 
#                 deleted=False
#             ).order_by('-admission_number').first()
            
#             if last_student and last_student.admission_number:
#                 try:
#                     # Try to extract and increment the number
#                     last_num = last_student.admission_number
#                     if '-' in last_num:
#                         last_id = int(last_num.split('-')[-1])
#                         new_id = f"ADM-{current_year}-{last_id + 1:04d}"
#                     else:
#                         # If format is different, just append sequence
#                         new_id = f"ADM-{current_year}-0001"
#                 except (ValueError, IndexError):
#                     new_id = f"ADM-{current_year}-0001"
#             else:
#                 new_id = f"ADM-{current_year}-0001"
            
#             attrs['admission_number'] = new_id
        
#         # Set admission date to current date if not provided
#         if not attrs.get('admission_date') and not self.instance:
#             attrs['admission_date'] = timezone.now().date()
        
#         return attrs
    
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
#         data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
#         # Add user data if user exists
#         if instance.user:
#             data['user'] = {
#                 'id': instance.user.id,
#                 'full_name': instance.user.full_name,
#                 'email': instance.user.email,
#                 'mobile': instance.user.mobile
#             }
        
#         return data


# class StudentListingSerializer(serializers.ModelSerializer):
#     """Simplified serializer for student listings"""
#     full_name = serializers.SerializerMethodField()
#     email = serializers.SerializerMethodField()
#     mobile = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Student
#         fields = ['id', 'admission_number', 'roll_number', 'full_name', 'email', 'mobile', 'gender', 'status']
    
#     def get_full_name(self, obj):
#         """Get full name from user if exists, otherwise from student data"""
#         if obj.user and obj.user.full_name:
#             return obj.user.full_name
#         # If no user linked, you might want to store name in Student model
#         # or return admission number as identifier
#         return f"Student {obj.admission_number}"
    
#     def get_email(self, obj):
#         """Get email from user if exists"""
#         return obj.user.email if obj.user else None
    
#     def get_mobile(self, obj):
#         """Get mobile from user if exists"""
#         return obj.user.mobile if obj.user else None


# class TeacherSerializer(serializers.ModelSerializer):
#     """Full teacher serializer with validations"""
    
#     class Meta:
#         model = Teacher
#         exclude = ['deleted']
#         read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
#     def validate_employee_id(self, value):
#         """Validate employee ID"""
#         if not value.strip():
#             raise serializers.ValidationError("Employee ID is required")
        
#         # Check for duplicate employee IDs
#         qs = Teacher.objects.filter(employee_id__iexact=value.strip(), deleted=False)
#         if self.instance:
#             qs = qs.exclude(id=self.instance.id)
        
#         if qs.exists():
#             raise serializers.ValidationError(f"Teacher with employee ID '{value}' already exists")
        
#         return value.strip().upper()
    
#     def validate_qualification(self, value):
#         """Validate qualification"""
#         if not value.strip():
#             raise serializers.ValidationError("Qualification is required")
        
#         if len(value) > 255:
#             raise serializers.ValidationError("Qualification cannot exceed 255 characters")
#         return value.strip()
    
#     def validate_specialization(self, value):
#         """Validate specialization"""
#         if value and len(value) > 255:
#             raise serializers.ValidationError("Specialization cannot exceed 255 characters")
#         return value.strip() if value else value
    
#     def validate_experience_years(self, value):
#         """Validate experience years"""
#         if value and value < 0:
#             raise serializers.ValidationError("Experience cannot be negative")
        
#         if value and value > 50:
#             raise serializers.ValidationError("Experience years seem too high")
#         return value
    
#     def validate_joining_date(self, value):
#         """Validate joining date"""
#         if value:
#             if value > timezone.now().date():
#                 raise serializers.ValidationError("Joining date cannot be in the future")
#         return value
    
#     def validate_salary(self, value):
#         """Validate salary"""
#         if value and value < 0:
#             raise serializers.ValidationError("Salary cannot be negative")
#         return value
    
#     def validate(self, attrs):
#         """Cross-field validation"""
#         # Auto-generate employee ID if not provided
#         if not attrs.get('employee_id') and not self.instance:
#             current_year = timezone.now().year
#             last_teacher = Teacher.objects.filter(
#                 joining_date__year=current_year, 
#                 deleted=False
#             ).order_by('-employee_id').first()
            
#             if last_teacher and last_teacher.employee_id:
#                 try:
#                     last_id = int(last_teacher.employee_id.split('-')[-1])
#                     new_id = f"EMP-{current_year}-{last_id + 1:04d}"
#                 except (ValueError, IndexError):
#                     new_id = f"EMP-{current_year}-0001"
#             else:
#                 new_id = f"EMP-{current_year}-0001"
            
#             attrs['employee_id'] = new_id
        
#         # Set joining date to current date if not provided
#         if not attrs.get('joining_date') and not self.instance:
#             attrs['joining_date'] = timezone.now().date()
        
#         return attrs
    
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
#         data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
#         # Add user data if user exists
#         if instance.user:
#             data['user'] = {
#                 'id': instance.user.id,
#                 'full_name': instance.user.full_name,
#                 'email': instance.user.email,
#                 'mobile': instance.user.mobile
#             }
        
#         return data

# class ParentSerializer(serializers.ModelSerializer):
#     """Full parent serializer with validations"""
#     children_list = serializers.SerializerMethodField()
#     children_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Parent
#         exclude = ['deleted']
#         read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
#     def get_children_list(self, obj):
#         return StudentListingSerializer(obj.students.filter(deleted=False), many=True).data
    
#     def get_children_count(self, obj):
#         return obj.students.filter(deleted=False).count()
    
#     def validate_relation(self, value):
#         """Validate relation"""
#         if not value.strip():
#             raise serializers.ValidationError("Relation is required")
        
#         valid_relations = ['father', 'mother', 'guardian']
#         if value not in valid_relations:
#             raise serializers.ValidationError(f"Relation must be one of: {', '.join(valid_relations)}")
        
#         return value.strip()
    
#     def validate_occupation(self, value):
#         """Validate occupation"""
#         if value and len(value) > 100:
#             raise serializers.ValidationError("Occupation cannot exceed 100 characters")
#         return value.strip() if value else value
    
#     def validate_annual_income(self, value):
#         """Validate annual income"""
#         if value and value < 0:
#             raise serializers.ValidationError("Annual income cannot be negative")
#         return value
    
#     def validate_office_address(self, value):
#         """Validate office address"""
#         if value and len(value) > 500:
#             raise serializers.ValidationError("Office address cannot exceed 500 characters")
#         return value.strip() if value else value
    
#     def validate(self, attrs):
#         """Cross-field validation"""
#         # Validate that students are provided
#         students = attrs.get('students', [])
#         if not students and not self.instance:
#             raise serializers.ValidationError({
#                 "students": "At least one student must be associated with the parent"
#             })
        
#         # Validate maximum number of students per parent
#         if students and len(students) > 10:
#             raise serializers.ValidationError({
#                 "students": "A parent cannot be associated with more than 10 students"
#             })
        
#         return attrs
    
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
#         data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
#         # Add user data if user exists
#         if instance.user:
#             data['user'] = {
#                 'id': instance.user.id,
#                 'full_name': instance.user.full_name,
#                 'email': instance.user.email,
#                 'mobile': instance.user.mobile
#             }
        
#         return data


class StudentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for student listings"""
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'roll_number', 'full_name', 
                  'email', 'mobile', 'gender', 'status']
    
    def get_full_name(self, obj):
        if obj.user and obj.user.full_name:
            return obj.user.full_name
        return f"Student {obj.admission_number}"
    
    def get_email(self, obj):
        return obj.user.email if obj.user else None
    
    def get_mobile(self, obj):
        return obj.user.mobile if obj.user else None


class StudentSerializer(serializers.ModelSerializer):
    """Full student serializer with user linking"""
    guardian_count = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Student
        exclude = ['deleted', 'user']  # Exclude user, handle via user_id
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'admission_number')
    
    def get_guardian_count(self, obj):
        return obj.parents.filter(deleted=False).count()
    
    def validate_user_id(self, value):
        """Validate user exists and can be linked"""
        if value:
            try:
                user = User.objects.get(id=value, deleted=False)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
            
            # Check if user already has a student profile
            existing_student = Student.objects.filter(user=user, deleted=False).first()
            if existing_student:
                if not self.instance or self.instance.id != existing_student.id:
                    raise serializers.ValidationError(
                        "This user already has a student profile"
                    )
            
            # Check if user has teacher profile
            existing_teacher = Teacher.objects.filter(user=user, deleted=False).first()
            if existing_teacher:
                raise serializers.ValidationError("This user is already a teacher")
            
            # Check if user has parent profile
            existing_parent = Parent.objects.filter(user=user, deleted=False).first()
            if existing_parent:
                raise serializers.ValidationError("This user is already a parent")
        
        return value
    
    def validate_roll_number(self, value):
        """Validate roll number uniqueness"""
        if value:
            qs = Student.objects.filter(
                roll_number__iexact=value.strip(), 
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"Student with roll number '{value}' already exists"
                )
            return value.strip()
        return value
    
    def validate_admission_date(self, value):
        """Validate admission date is not in future"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Admission date cannot be in the future")
        return value
    
    def validate_gender(self, value):
        """Validate gender choice"""
        valid_choices = ['M', 'F', 'O']
        if value and value not in valid_choices:
            raise serializers.ValidationError(
                f"Gender must be one of: {', '.join(valid_choices)}"
            )
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Set admission date to current date if not provided (only on create)
        if not attrs.get('admission_date') and not self.instance:
            attrs['admission_date'] = timezone.now().date()
        
        # Gender is required
        if not self.instance and not attrs.get('gender'):
            raise serializers.ValidationError({"gender": "Gender is required"})
        
        return attrs
    
    def _generate_admission_number(self):
        """Generate unique admission number"""
        current_year = timezone.now().year
        last_student = Student.objects.filter(deleted=False).order_by('-id').first()
        new_num = (last_student.id + 1) if last_student else 1
        return f"ADM-{current_year}-{new_num:04d}"
    
    @transaction.atomic
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        
        # Auto-generate admission number
        validated_data['admission_number'] = self._generate_admission_number()
        
        # Create student
        student = Student.objects.create(**validated_data)
        
        # Link user if provided
        if user_id:
            user = User.objects.get(id=user_id, deleted=False)
            student.user = user
            student.save(update_fields=['user'])
            # Update user type
            user.type = STUDENT
            user.save(update_fields=['type', 'updated_at'])
        
        return student
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None)
        
        # Remove admission_number from validated_data if present (shouldn't be updated)
        validated_data.pop('admission_number', None)
        
        # Handle user linking/unlinking
        if user_id is not None:
            current_user_id = instance.user.id if instance.user else None
            
            if user_id != current_user_id:
                # Reset old user type
                if instance.user:
                    old_user = instance.user
                    old_user.type = None
                    old_user.save(update_fields=['type', 'updated_at'])
                
                if user_id:
                    # Link new user
                    new_user = User.objects.get(id=user_id, deleted=False)
                    instance.user = new_user
                    new_user.type = STUDENT
                    new_user.save(update_fields=['type', 'updated_at'])
                else:
                    # Unlink user
                    instance.user = None
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
        data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'full_name': instance.user.full_name,
                'email': instance.user.email,
                'mobile': instance.user.mobile,
                'is_active': instance.user.is_active,
                'is_verified': instance.user.is_verified,
            }
        else:
            data['user'] = None
        
        return data

class TeacherListSerializer(serializers.ModelSerializer):
    """Minimal serializer for teacher listings in dropdowns/references"""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_mobile = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = [
            'id', 
            'employee_id', 
            'user_name',
            'user_email',
            'user_mobile',
            'designation',
            'qualification',
            'specialization',
            'experience_years',
            'is_class_teacher'
        ]
    
    def get_user_name(self, obj):
        """Get user's full name"""
        if obj.user and not obj.user.deleted:
            return obj.user.get_full_name()
        return None
    
    def get_user_email(self, obj):
        """Get user's email"""
        if obj.user and not obj.user.deleted:
            return obj.user.email
        return None
    
    def get_user_mobile(self, obj):
        """Get user's mobile"""
        if obj.user and not obj.user.deleted:
            return obj.user.mobile
        return None
    
    def to_representation(self, instance):
        """Custom representation for listing"""
        # Handle soft-deleted instances
        if instance.deleted:
            return {
                'id': instance.id,
                'employee_id': instance.employee_id,
                'user_name': 'Deleted Teacher',
                'message': f'Teacher "{instance.employee_id}" has been deleted'
            }
        
        data = super().to_representation(instance)
        
        # Format for better display in dropdowns
        if data['user_name']:
            data['display_name'] = f"{data['user_name']} ({data['employee_id']}) - {data['designation']}"
        else:
            data['display_name'] = f"{data['employee_id']} - {data['designation']}"
        
        return data

class TeacherSerializer(serializers.ModelSerializer):
    """Full teacher serializer with user linking"""
    user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Teacher
        exclude = ['deleted', 'user']  # Exclude user, handle via user_id
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def validate_user_id(self, value):
        """Validate user exists and can be linked"""
        if value:
            try:
                user = User.objects.get(id=value, deleted=False)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
            
            # Check if user already has a teacher profile
            existing_teacher = Teacher.objects.filter(user=user, deleted=False).first()
            if existing_teacher:
                if not self.instance or self.instance.id != existing_teacher.id:
                    raise serializers.ValidationError(
                        "This user already has a teacher profile"
                    )
            
            # Check if user is a student (not allowed)
            existing_student = Student.objects.filter(user=user, deleted=False).first()
            if existing_student:
                raise serializers.ValidationError("This user is already a student")
            
            # Note: Teacher CAN also be a parent - no check needed
        
        return value
    
    def validate_employee_id(self, value):
        """Validate employee ID uniqueness"""
        if not value or not value.strip():
            raise serializers.ValidationError("Employee ID is required")
        
        qs = Teacher.objects.filter(
            employee_id__iexact=value.strip(), 
            deleted=False
        )
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(
                f"Teacher with employee ID '{value}' already exists"
            )
        
        return value.strip().upper()
    
    def validate_qualification(self, value):
        """Validate qualification - required field"""
        if not value or not value.strip():
            raise serializers.ValidationError("Qualification is required")
        if len(value) > 255:
            raise serializers.ValidationError("Qualification cannot exceed 255 characters")
        return value.strip()
    
    def validate_designation(self, value):
        """Validate designation - required field"""
        if not value or not value.strip():
            raise serializers.ValidationError("Designation is required")
        if len(value) > 100:
            raise serializers.ValidationError("Designation cannot exceed 100 characters")
        return value.strip()
    
    def validate_experience_years(self, value):
        """Validate experience years"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Experience cannot be negative")
            if value > 50:
                raise serializers.ValidationError("Experience years seem too high")
        return value or 0  # Default to 0
    
    def validate_joining_date(self, value):
        """Validate joining date"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Joining date cannot be in the future")
        return value
    
    def validate_salary(self, value):
        """Validate salary"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
    
    def validate(self, attrs):
        """Cross-field validation and auto-generation"""
        # Auto-generate employee ID if not provided (only on create)
        if not attrs.get('employee_id') and not self.instance:
            current_year = timezone.now().year
            last_teacher = Teacher.objects.filter(deleted=False).order_by('-id').first()
            new_num = (last_teacher.id + 1) if last_teacher else 1
            attrs['employee_id'] = f"EMP-{current_year}-{new_num:04d}"
        
        # Set joining date to current date if not provided (only on create)
        if not attrs.get('joining_date') and not self.instance:
            attrs['joining_date'] = timezone.now().date()
        
        # Required fields check for create
        if not self.instance:
            if not attrs.get('qualification'):
                raise serializers.ValidationError({"qualification": "Qualification is required"})
            if not attrs.get('designation'):
                raise serializers.ValidationError({"designation": "Designation is required"})
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        
        teacher = Teacher.objects.create(**validated_data)
        
        if user_id:
            user = User.objects.get(id=user_id, deleted=False)
            teacher.user = user
            teacher.save(update_fields=['user'])
            user.type = TEACHER
            user.is_staff = True  # Teachers get staff access
            user.save(update_fields=['type', 'is_staff', 'updated_at'])
        
        return teacher
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None)
        
        if user_id is not None:
            current_user_id = instance.user.id if instance.user else None
            
            if user_id != current_user_id:
                # Reset old user
                if instance.user:
                    old_user = instance.user
                    old_user.type = None
                    old_user.is_staff = False
                    old_user.save(update_fields=['type', 'is_staff', 'updated_at'])
                
                if user_id:
                    new_user = User.objects.get(id=user_id, deleted=False)
                    instance.user = new_user
                    new_user.type = TEACHER
                    new_user.is_staff = True
                    new_user.save(update_fields=['type', 'is_staff', 'updated_at'])
                else:
                    instance.user = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
        data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'full_name': instance.user.full_name,
                'email': instance.user.email,
                'mobile': instance.user.mobile,
                'is_active': instance.user.is_active,
                'is_verified': instance.user.is_verified,
            }
        else:
            data['user'] = None
        
        return data


class ParentSerializer(serializers.ModelSerializer):
    """Full parent serializer with user linking"""
    children_list = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Parent
        exclude = ['deleted', 'user', 'students']  # Handle via user_id and student_ids
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_children_list(self, obj):
        return StudentListingSerializer(
            obj.students.filter(deleted=False), 
            many=True
        ).data
    
    def get_children_count(self, obj):
        return obj.students.filter(deleted=False).count()
    
    def validate_user_id(self, value):
        """Validate user exists and can be linked"""
        if value:
            try:
                user = User.objects.get(id=value, deleted=False)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
            
            # Check if user already has a parent profile
            existing_parent = Parent.objects.filter(user=user, deleted=False).first()
            if existing_parent:
                if not self.instance or self.instance.id != existing_parent.id:
                    raise serializers.ValidationError(
                        "This user already has a parent profile"
                    )
            
            # Check if user is a student (not allowed)
            existing_student = Student.objects.filter(user=user, deleted=False).first()
            if existing_student:
                raise serializers.ValidationError("This user is already a student")
            
            # Note: Parent CAN also be a teacher - no check needed
        
        return value
    
    def validate_student_ids(self, value):
        """Validate student IDs exist"""
        if value:
            existing_ids = set(
                Student.objects.filter(id__in=value, deleted=False)
                .values_list('id', flat=True)
            )
            missing = set(value) - existing_ids
            if missing:
                raise serializers.ValidationError(
                    f"Students with IDs {list(missing)} not found"
                )
            if len(value) > 10:
                raise serializers.ValidationError(
                    "A parent cannot be associated with more than 10 students"
                )
        return value
    
    def validate_relation(self, value):
        """Validate relation type - matches model choices"""
        if not value or not value.strip():
            raise serializers.ValidationError("Relation is required")
        
        valid_relations = ['father', 'mother', 'guardian']
        if value.lower() not in valid_relations:
            raise serializers.ValidationError(
                f"Relation must be one of: {', '.join(valid_relations)}"
            )
        return value.strip().lower()
    
    def validate_occupation(self, value):
        """Validate occupation"""
        if value and len(value) > 100:
            raise serializers.ValidationError("Occupation cannot exceed 100 characters")
        return value.strip() if value else ''
    
    def validate_annual_income(self, value):
        """Validate annual income"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Annual income cannot be negative")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        student_ids = attrs.get('student_ids')
        
        # Require at least one student on create
        if not self.instance and not student_ids:
            raise serializers.ValidationError({
                "student_ids": "At least one student must be associated with the parent"
            })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        student_ids = validated_data.pop('student_ids', [])
        
        parent = Parent.objects.create(**validated_data)
        
        # Link user if provided
        if user_id:
            user = User.objects.get(id=user_id, deleted=False)
            parent.user = user
            parent.save(update_fields=['user'])
            # Only update type if not already a teacher
            if user.type != TEACHER:
                user.type = PARENT
                user.save(update_fields=['type', 'updated_at'])
        
        # Link students (ManyToMany)
        if student_ids:
            students = Student.objects.filter(id__in=student_ids, deleted=False)
            parent.students.set(students)
        
        return parent
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None)
        student_ids = validated_data.pop('student_ids', None)
        
        # Handle user linking/unlinking
        if user_id is not None:
            current_user_id = instance.user.id if instance.user else None
            
            if user_id != current_user_id:
                # Reset old user type (only if they were PARENT type)
                if instance.user and instance.user.type == PARENT:
                    old_user = instance.user
                    old_user.type = None
                    old_user.save(update_fields=['type', 'updated_at'])
                
                if user_id:
                    new_user = User.objects.get(id=user_id, deleted=False)
                    instance.user = new_user
                    if new_user.type != TEACHER:
                        new_user.type = PARENT
                        new_user.save(update_fields=['type', 'updated_at'])
                else:
                    instance.user = None
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update students if provided
        if student_ids is not None:
            students = Student.objects.filter(id__in=student_ids, deleted=False)
            instance.students.set(students)
        
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.get_full_name() if instance.created_by else None
        data['updated_by'] = instance.updated_by.get_full_name() if instance.updated_by else None
        
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'full_name': instance.user.full_name,
                'email': instance.user.email,
                'mobile': instance.user.mobile,
                'is_active': instance.user.is_active,
                'is_verified': instance.user.is_verified,
            }
        else:
            data['user'] = None
        
        return data