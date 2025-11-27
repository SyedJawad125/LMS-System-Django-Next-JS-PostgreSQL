from django.db import models
from apps.academic.models import AcademicYear, Section, Subject
from apps.users.models import Teacher
from utils.reusable_classes import TimeUserStamps

# Create your models here.
class TimeSlot(TimeUserStamps):
    """Period/Class Timings"""
    name = models.CharField(max_length=50)  # Period 1, Period 2, etc.
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    order = models.IntegerField()
    
    class Meta:
        db_table = 'time_slots'
        ordering = ['order']


class Timetable(TimeUserStamps):
    """Class Timetable"""
    DAYS = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    )
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetables')
    day = models.CharField(max_length=10, choices=DAYS)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    room = models.CharField(max_length=50, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'timetables'
        unique_together = ['section', 'day', 'time_slot', 'academic_year']