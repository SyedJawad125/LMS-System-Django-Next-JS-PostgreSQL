from django.db import models
from apps.academic.models import Subject
from apps.users.models import Student, Teacher
from utils.enums import *
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class Course(TimeUserStamps):
    """Online Courses"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True)
    duration_hours = models.IntegerField()
    level = models.CharField(max_length=20, choices=(
        (BEGINNER, BEGINNER),
        (INTERMEDIATE, INTERMEDIATE),
        (ADVANCED, ADVANCED),
    ))
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'courses'


class Lesson(TimeUserStamps):
    """Course Lessons/Modules"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='lessons/videos/', null=True, blank=True)
    duration_minutes = models.IntegerField()
    order = models.IntegerField()
    attachments = models.FileField(upload_to='lessons/attachments/', null=True, blank=True)
    is_preview = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['order']


class CourseEnrollment(TimeUserStamps):
    """Student Course Enrollments"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'course_enrollments'
        unique_together = ['student', 'course']


class LessonProgress(TimeUserStamps):
    """Student Lesson Progress"""
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    time_spent_minutes = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['enrollment', 'lesson']


class Quiz(TimeUserStamps):
    """Quizzes/Online Tests"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    duration_minutes = models.IntegerField()
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    attempts_allowed = models.IntegerField(default=1)
    is_published = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        db_table = 'quizzes'


class Question(TimeUserStamps):
    """Quiz Questions"""
    QUESTION_TYPES = (
        (MCQ, MCQ),
        (TRUE_FALSE, TRUE_FALSE),
        (SHORT_ANSWER, SHORT_ANSWER),
        (ESSAY, ESSAY),
)
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField()
    order = models.IntegerField()
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['order']


class QuestionOption(TimeUserStamps):
    """MCQ Options"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()
    
    class Meta:
        db_table = 'question_options'
        ordering = ['order']


class QuizAttempt(TimeUserStamps):
    """Student Quiz Attempts"""
    STATUS_CHOICES = (
        (IN_PROGRESS, IN_PROGRESS),
        (SUBMITTED, SUBMITTED),
        (GRADED, GRADED),
)
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attempt_number = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'quiz_attempts'
        unique_together = ['quiz', 'student', 'attempt_number']


class QuizAnswer(TimeUserStamps):
    """Student Quiz Answers"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    marks_awarded = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'quiz_answers'