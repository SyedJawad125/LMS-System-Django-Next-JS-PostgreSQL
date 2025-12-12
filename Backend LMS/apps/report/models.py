from django.db import models
from apps.academic.models import AcademicYear
from apps.exams.models import Exam
from apps.users.models import Student, Teacher
from utils.enums import *
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class ReportCard(TimeUserStamps):
    """Student Report Cards"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='report_cards')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    rank_in_class = models.IntegerField(null=True, blank=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_cards'
        unique_together = ['student', 'exam']


class StudentBehavior(TimeUserStamps):
    """Behavior/Conduct Records"""
    BEHAVIOR_TYPES = (
        (POSITIVE, POSITIVE),
        (NEGATIVE, NEGATIVE),
        (NEUTRAL, NEUTRAL),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='behavior_records')
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_date = models.DateField()
    reported_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    action_taken = models.TextField(blank=True)
    points = models.IntegerField(default=0)  # Merit/Demerit points
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_behavior'
