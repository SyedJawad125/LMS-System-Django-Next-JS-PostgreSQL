import datetime
import uuid
from django.db import models
from utils.reusable_classes import TimeStamps, TimeUserStamps
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from utils.validators import val_name, val_mobile, val_code_name
from utils.enums import *


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('User must have a username.')
        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def get_profile_image_path(self, filename):
    return f'profile_images/{self.pk}/{str(uuid.uuid4())}.png'


class User(AbstractBaseUser, TimeStamps):
    type_choices = (
    (CUSTOMER, CUSTOMER),
    (EMPLOYEE, EMPLOYEE),
    (STUDENT, STUDENT),
    (TEACHER, TEACHER),
    (PARENT, PARENT),
)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, validators=[val_name])
    last_name = models.CharField(max_length=100, validators=[val_name])
    full_name = models.CharField(max_length=200, validators=[val_name], null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=35, validators=[val_mobile], null=True, blank=True)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_path, null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    password_link_token = models.CharField(max_length=255, null=True, blank=True)
    password_link_token_created_at = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    last_password_changed = models.DateTimeField(null=True, blank=True)
    role = models.ForeignKey('Role', related_name='role_users', blank=True, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=type_choices, default=CUSTOMER)
    activation_link_token = models.CharField(max_length=255, null=True, blank=True)
    activation_link_token_created_at = models.DateTimeField(null=True, blank=True)
    deactivated = models.BooleanField(default=False)
    password = models.CharField(max_length=128, null=True, blank=True)
    objects = UserManager()
    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        self.email = self.username
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.full_name = f'{self.first_name} {self.last_name}'
        return super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

class Role(TimeUserStamps):
    name = models.CharField(max_length=100, validators=[val_name])
    code_name = models.CharField(max_length=50, unique=True, validators=[val_code_name])
    permissions = models.ManyToManyField('Permission', related_name='+')
    description = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        return super().save(*args, **kwargs)


class Permission(models.Model):
    name = models.CharField(max_length=100, validators=[val_name])
    code_name = models.CharField(max_length=100, unique=True, validators=[val_code_name])
    module_name = models.CharField(max_length=100)
    module_label = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class UserToken(TimeStamps):
    user = models.ForeignKey('User', on_delete=models.PROTECT, related_name="user_token")
    device_token = models.TextField(max_length=512, null=True, blank=True)


# class Employee(TimeUserStamps):
#     status_choices = (
#         (INVITED, INVITED),
#         (ACTIVE, ACTIVE),
#         (DEACTIVATED, DEACTIVATED),
#     )
#     user = models.OneToOneField('User', on_delete=models.SET_NULL, related_name="user_employee", null=True, blank=True)
#     status = models.CharField(max_length=20, choices=status_choices, default=INVITED)



class Employee(TimeUserStamps):
    status_choices = (
        (INVITED, INVITED),
        (ACTIVE, ACTIVE),
        (DEACTIVATED, DEACTIVATED),
    )
    
    user = models.OneToOneField(
        'User', 
        on_delete=models.SET_NULL, 
        related_name="user_employee", 
        null=True, 
        blank=True
    )
    employee_id = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=status_choices, default=INVITED)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.full_name if self.user else 'No User'}"
    
    def generate_employee_id(self):
        """Generate a unique employee ID in format: EMP2024-000001"""
        current_year = datetime.datetime.now().year
        
        # Get the highest sequence number for current year
        employees_this_year = Employee.objects.filter(
            employee_id__startswith=f"EMP{current_year}"
        ).order_by('-employee_id')
        
        if employees_this_year.exists():
            # Extract sequence numbers and find max
            max_sequence = 0
            for emp in employees_this_year:
                try:
                    # For format EMP2024-000123
                    parts = emp.employee_id.split('-')
                    if len(parts) == 2:
                        seq = int(parts[1])
                        max_sequence = max(max_sequence, seq)
                except (ValueError, IndexError):
                    continue
            
            sequence = max_sequence + 1
        else:
            sequence = 1
        
        return f"EMP{current_year}-{sequence:06d}"
    
    def save(self, *args, **kwargs):
        # Generate employee_id only if it doesn't exist
        if not self.employee_id:
            max_attempts = 10
            for attempt in range(max_attempts):
                new_id = self.generate_employee_id()
                if not Employee.objects.filter(employee_id=new_id).exists():
                    self.employee_id = new_id
                    break
                if attempt == max_attempts - 1:
                    # Fallback: use timestamp
                    timestamp = int(datetime.datetime.now().timestamp())
                    self.employee_id = f"EMP{timestamp}"
        
        super().save(*args, **kwargs)


class Student(TimeUserStamps):
    """Student Profile"""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('dropout', 'Dropout'),
        ('transferred', 'Transferred'),
        ('inactive', 'Inactive'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    admission_number = models.CharField(max_length=50, unique=True)
    roll_number = models.CharField(max_length=50, blank=True)
    # academic_year = models.ForeignKey('AcademicYear', on_delete=models.SET_NULL, null=True)
    # class_enrolled = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True)
    # section = models.ForeignKey('Section', on_delete=models.SET_NULL, null=True)
    admission_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100, blank=True)
    religion = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, blank=True)  # General, SC, ST, OBC
    previous_school = models.CharField(max_length=255, blank=True)
    medical_conditions = models.TextField(blank=True)
    is_hostel_resident = models.BooleanField(default=False)
    is_transport_required = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        db_table = 'students'
        ordering = ['admission_number']
    
    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name() if self.user else 'No User'}"

# class Teacher(TimeUserStamps):
#     """Teacher Profile"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
#     employee_id = models.CharField(max_length=50, unique=True)
#     qualification = models.CharField(max_length=255)
#     specialization = models.CharField(max_length=255, blank=True)
#     experience_years = models.IntegerField(default=0)
#     joining_date = models.DateField()
#     designation = models.CharField(max_length=100)
#     # department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
#     salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     is_class_teacher = models.BooleanField(default=False)
    
#     class Meta:
#         db_table = 'teachers'


class Teacher(TimeUserStamps):
    """Teacher Profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='teacher_profile', null=True, blank=True)
    employee = models.OneToOneField('Employee', on_delete=models.CASCADE, 
                                   related_name='teacher', null=True, blank=True)
    qualification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.IntegerField(default=0)
    joining_date = models.DateField()
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_class_teacher = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'teachers'
    
    def save(self, *args, **kwargs):
        # Auto-create Employee record if creating a new Teacher without one
        if not self.pk and not self.employee:
            employee = Employee.objects.create(user=self.user, status=ACTIVE)
            self.employee = employee
        
        super().save(*args, **kwargs)
    
    @property
    def employee_id(self):
        """Get employee_id from Employee model - Read only property"""
        return self.employee.employee_id if self.employee else None
    
    def get_employee_id_display(self):
        """Display employee ID"""
        return self.employee_id or "Not assigned"
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() if self.user else 'No User'}"


class Parent(TimeUserStamps):
    """Parent/Guardian Profile"""
    RELATION_CHOICES = (
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile', null=True, blank=True)
    students = models.ManyToManyField(Student, related_name='parents')
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    occupation = models.CharField(max_length=100, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    office_address = models.TextField(blank=True)
    
    class Meta:
        db_table = 'parents'