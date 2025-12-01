import django_filters as filters
from django.db.models import Q
from .models import (
    Course, Lesson, CourseEnrollment, LessonProgress, 
    Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer
)


class CourseFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    subject = filters.NumberFilter(field_name='subject')
    teacher = filters.NumberFilter(field_name='teacher')
    level = filters.CharFilter(field_name='level')
    is_published = filters.BooleanFilter(field_name='is_published')
    duration_hours_min = filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
    duration_hours_max = filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')
    created_at_start = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_end = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Course
        fields = ['title', 'subject', 'teacher', 'level', 'is_published']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )


class LessonFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    course = filters.NumberFilter(field_name='course')
    content = filters.CharFilter(field_name='content', lookup_expr='icontains')
    is_preview = filters.BooleanFilter(field_name='is_preview')
    order_min = filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_max = filters.NumberFilter(field_name='order', lookup_expr='lte')
    duration_minutes_min = filters.NumberFilter(field_name='duration_minutes', lookup_expr='gte')
    duration_minutes_max = filters.NumberFilter(field_name='duration_minutes', lookup_expr='lte')
    
    class Meta:
        model = Lesson
        fields = ['title', 'course', 'is_preview', 'order']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(content__icontains=value)
        )


class CourseEnrollmentFilter(filters.FilterSet):
    student = filters.NumberFilter(field_name='student')
    course = filters.NumberFilter(field_name='course')
    progress_percentage_min = filters.NumberFilter(field_name='progress_percentage', lookup_expr='gte')
    progress_percentage_max = filters.NumberFilter(field_name='progress_percentage', lookup_expr='lte')
    certificate_issued = filters.BooleanFilter(field_name='certificate_issued')
    enrolled_at_start = filters.DateFilter(field_name='enrolled_at', lookup_expr='gte')
    enrolled_at_end = filters.DateFilter(field_name='enrolled_at', lookup_expr='lte')
    completed_at_start = filters.DateFilter(field_name='completed_at', lookup_expr='gte')
    completed_at_end = filters.DateFilter(field_name='completed_at', lookup_expr='lte')
    completed = filters.BooleanFilter(method='filter_completed')
    
    class Meta:
        model = CourseEnrollment
        fields = ['student', 'course', 'certificate_issued']
    
    def filter_completed(self, queryset, name, value):
        if value:
            return queryset.filter(completed_at__isnull=False)
        else:
            return queryset.filter(completed_at__isnull=True)


class LessonProgressFilter(filters.FilterSet):
    enrollment = filters.NumberFilter(field_name='enrollment')
    lesson = filters.NumberFilter(field_name='lesson')
    is_completed = filters.BooleanFilter(field_name='is_completed')
    time_spent_minutes_min = filters.NumberFilter(field_name='time_spent_minutes', lookup_expr='gte')
    time_spent_minutes_max = filters.NumberFilter(field_name='time_spent_minutes', lookup_expr='lte')
    last_accessed_start = filters.DateTimeFilter(field_name='last_accessed', lookup_expr='gte')
    last_accessed_end = filters.DateTimeFilter(field_name='last_accessed', lookup_expr='lte')
    completed_at_start = filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_at_end = filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    
    class Meta:
        model = LessonProgress
        fields = ['enrollment', 'lesson', 'is_completed']


class QuizFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    course = filters.NumberFilter(field_name='course')
    lesson = filters.NumberFilter(field_name='lesson')
    subject = filters.NumberFilter(field_name='subject')
    teacher = filters.NumberFilter(field_name='teacher')
    is_published = filters.BooleanFilter(field_name='is_published')
    duration_minutes_min = filters.NumberFilter(field_name='duration_minutes', lookup_expr='gte')
    duration_minutes_max = filters.NumberFilter(field_name='duration_minutes', lookup_expr='lte')
    total_marks_min = filters.NumberFilter(field_name='total_marks', lookup_expr='gte')
    total_marks_max = filters.NumberFilter(field_name='total_marks', lookup_expr='lte')
    passing_marks_min = filters.NumberFilter(field_name='passing_marks', lookup_expr='gte')
    passing_marks_max = filters.NumberFilter(field_name='passing_marks', lookup_expr='lte')
    start_date_start = filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    start_date_end = filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')
    end_date_start = filters.DateTimeFilter(field_name='end_date', lookup_expr='gte')
    end_date_end = filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')
    
    class Meta:
        model = Quiz
        fields = ['title', 'course', 'lesson', 'subject', 'teacher', 'is_published']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )


class QuestionFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    question_text = filters.CharFilter(field_name='question_text', lookup_expr='icontains')
    quiz = filters.NumberFilter(field_name='quiz')
    question_type = filters.CharFilter(field_name='question_type')
    marks_min = filters.NumberFilter(field_name='marks', lookup_expr='gte')
    marks_max = filters.NumberFilter(field_name='marks', lookup_expr='lte')
    order_min = filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_max = filters.NumberFilter(field_name='order', lookup_expr='lte')
    
    class Meta:
        model = Question
        fields = ['quiz', 'question_type']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(question_text__icontains=value)
        )


class QuestionOptionFilter(filters.FilterSet):
    question = filters.NumberFilter(field_name='question')
    option_text = filters.CharFilter(field_name='option_text', lookup_expr='icontains')
    is_correct = filters.BooleanFilter(field_name='is_correct')
    order_min = filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_max = filters.NumberFilter(field_name='order', lookup_expr='lte')
    
    class Meta:
        model = QuestionOption
        fields = ['question', 'is_correct']


class QuizAttemptFilter(filters.FilterSet):
    quiz = filters.NumberFilter(field_name='quiz')
    student = filters.NumberFilter(field_name='student')
    attempt_number = filters.NumberFilter(field_name='attempt_number')
    status = filters.CharFilter(field_name='status')
    marks_obtained_min = filters.NumberFilter(field_name='marks_obtained', lookup_expr='gte')
    marks_obtained_max = filters.NumberFilter(field_name='marks_obtained', lookup_expr='lte')
    percentage_min = filters.NumberFilter(field_name='percentage', lookup_expr='gte')
    percentage_max = filters.NumberFilter(field_name='percentage', lookup_expr='lte')
    start_time_start = filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    start_time_end = filters.DateTimeFilter(field_name='start_time', lookup_expr='lte')
    end_time_start = filters.DateTimeFilter(field_name='end_time', lookup_expr='gte')
    end_time_end = filters.DateTimeFilter(field_name='end_time', lookup_expr='lte')
    
    class Meta:
        model = QuizAttempt
        fields = ['quiz', 'student', 'status']


class QuizAnswerFilter(filters.FilterSet):
    attempt = filters.NumberFilter(field_name='attempt')
    question = filters.NumberFilter(field_name='question')
    selected_option = filters.NumberFilter(field_name='selected_option')
    is_correct = filters.BooleanFilter(field_name='is_correct')
    marks_awarded_min = filters.NumberFilter(field_name='marks_awarded', lookup_expr='gte')
    marks_awarded_max = filters.NumberFilter(field_name='marks_awarded', lookup_expr='lte')
    
    class Meta:
        model = QuizAnswer
        fields = ['attempt', 'question', 'selected_option', 'is_correct']