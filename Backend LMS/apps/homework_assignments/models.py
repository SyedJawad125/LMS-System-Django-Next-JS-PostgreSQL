from django.db import models
from apps.academic.models import Class, Section, Subject
from apps.users.models import Student, Teacher
from utils.enums import *
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class Assignment(TimeUserStamps):
    """Homework/Assignments"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    assign_date = models.DateField()
    due_date = models.DateField()
    max_marks = models.IntegerField()
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-created_at']


class AssignmentSubmission(TimeUserStamps):
    """Student Assignment Submissions"""
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (SUBMITTED, SUBMITTED),
        (GRADED, GRADED),
        (LATE_SUBMISSION, LATE_SUBMISSION),
)
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='submissions/')
    submission_text = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'assignment_submissions'
        unique_together = ['assignment', 'student']