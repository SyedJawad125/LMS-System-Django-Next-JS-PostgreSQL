from django.db import models
from apps.users.models import Teacher
from utils.reusable_classes import TimeUserStamps

# Create your models here.


class AcademicYear(TimeUserStamps):
    """Academic Year Management"""
    name = models.CharField(max_length=50, unique=True)  # e.g., "2023-2024"
    code = models.CharField(max_length=20, null=True, blank=True)  # e.g., "2023-24"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'academic_years'
        ordering = ['-start_date']
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Auto-generate code from name or dates
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generate code from name or dates"""
        # Try to extract from name first
        if '-' in self.name:
            parts = self.name.split('-')
            if len(parts) >= 2:
                start_year = parts[0].strip()
                end_year = parts[1].strip()
                if len(end_year) == 4:
                    return f"{start_year}-{end_year[2:]}"
                return f"{start_year}-{end_year}"
        
        # Fallback to dates
        start_year = self.start_date.year
        end_year = self.end_date.year
        return f"{start_year}-{str(end_year)[-2:]}"
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(TimeUserStamps):
    """Academic Departments"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    head = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'departments'


class Class(TimeUserStamps):
    """Class/Grade Level"""
    name = models.CharField(max_length=50)  # e.g., "Grade 10", "Class XII"
    code = models.CharField(max_length=20, unique=True)
    level = models.IntegerField()  # 1-12 or custom
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'classes'
        verbose_name_plural = 'Classes'
        ordering = ['level']


class Section(TimeUserStamps):
    """Class Sections"""
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)  # A, B, C, etc.
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='class_teacher_sections')
    room_number = models.CharField(max_length=20, blank=True)
    capacity = models.IntegerField(default=40)
    
    class Meta:
        db_table = 'sections'
        unique_together = ['class_level', 'name', 'academic_year']


class Subject(TimeUserStamps):
    """Subjects/Courses"""
    SUBJECT_TYPES = (
        ('core', 'Core Subject'),
        ('elective', 'Elective'),
        ('optional', 'Optional'),
        ('extra', 'Extra Curricular'),
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    credit_hours = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'subjects'


class ClassSubject(TimeUserStamps):
    """Subject Assignment to Classes"""
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'class_subjects'
        unique_together = ['section', 'subject', 'academic_year']
