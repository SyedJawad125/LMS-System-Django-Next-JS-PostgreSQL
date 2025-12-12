from django.db import models

from apps.users.models import Student, User
from apps.academic.models import Class
from utils.enums import *
from utils.reusable_classes import TimeUserStamps


# Create your models here.

class Announcement(TimeUserStamps):
    """School Announcements"""
    ANNOUNCEMENT_TYPES = (
        (GENERAL, GENERAL),
        (URGENT, URGENT),
        (EVENT, EVENT),
        (HOLIDAY, HOLIDAY),
        (EXAM, EXAMINATION),
)
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES)
    target_audience = models.CharField(max_length=20, choices=(
        (ALL, ALL),
        (STUDENTS, STUDENTS),
        (PARENTS, PARENTS),
        (TEACHERS, TEACHERS),
        (SPECIFIC_CLASS, SPECIFIC_CLASS),
))
    target_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    attachment = models.FileField(upload_to='announcements/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-published_at']


class Event(TimeUserStamps):
    """School Events"""
    EVENT_TYPES = (
    (ACADEMIC, ACADEMIC),
    (SPORTS, SPORTS),
    (CULTURAL, CULTURAL),
    (EXCURSION, EXCURSION),
    (MEETING, MEETING),
    (OTHER, OTHER),
)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    target_classes = models.ManyToManyField(Class, blank=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['-start_date']


class Message(TimeUserStamps):
    """Internal Messaging System"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    attachment = models.FileField(upload_to='messages/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-sent_at']


class Notification(TimeUserStamps):
    """System Notifications"""
    NOTIFICATION_TYPES = (
        (FEE_DUE, FEE_DUE),
        (ATTENDANCE_LOW, ATTENDANCE_LOW),
        (EXAM_SCHEDULE, EXAM_SCHEDULE),
        (RESULT_PUBLISHED, RESULT_PUBLISHED),
        (ANNOUNCEMENT, ANNOUNCEMENT),
        (EVENT, EVENT),
        (MESSAGE, MESSAGE),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']