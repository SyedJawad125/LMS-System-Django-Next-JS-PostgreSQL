from django.db import models
from apps.academic.models import AcademicYear, Class, Subject
from apps.users.models import Student, Teacher
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class ExamType(TimeUserStamps):
    """Types of Examinations"""
    name = models.CharField(max_length=100)  # Mid-term, Final, Unit Test, etc.
    code = models.CharField(max_length=20)
    weightage = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'exam_types'


class Exam(TimeUserStamps):
    """Examination Schedule"""
    name = models.CharField(max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'exams'


class ExamSchedule(TimeUserStamps):
    """Individual Exam Paper Schedule"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    max_marks = models.IntegerField()
    min_passing_marks = models.IntegerField()
    
    class Meta:
        db_table = 'exam_schedules'


class ExamResult(TimeUserStamps):
    """Student Exam Results"""
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    is_absent = models.BooleanField(default=False)
    entered_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    entered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exam_results'
        unique_together = ['exam_schedule', 'student']


class GradeSystem(TimeUserStamps):
    """Grading System Configuration"""
    name = models.CharField(max_length=50)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'grade_systems'