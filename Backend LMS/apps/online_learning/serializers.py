from datetime import datetime
from django.utils import timezone  # Change this line
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    Course, Lesson, CourseEnrollment, LessonProgress, Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer
)
from apps.academic.serializers import SubjectListingSerializer
from apps.users.serializers import StudentListSerializer, TeacherListSerializer
# Remove these duplicate/circular imports:
# from .models import QuizAttempt, Quiz, Student  (already imported above)
# from apps.online_learning.serializers import QuizListingSerializer  (circular import)

# ==================== Course Serializers ====================

class CourseListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for course listings"""
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'teacher_name', 'subject_name', 
            'level', 'duration_hours', 'is_published', 'lessons_count'
        ]
    
    def get_teacher_name(self, obj):
        if obj.teacher and obj.teacher.user:
            full_name = obj.teacher.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.teacher.user.username
        return None
    
    def get_lessons_count(self, obj):
        if obj.deleted:
            return 0
        return obj.lessons.filter(deleted=False).count()


class CourseSerializer(serializers.ModelSerializer):
    """Full course serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    teacher_detail = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    enrolled_students_count = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'subject', 'teacher', 
            'thumbnail', 'duration_hours', 'level', 'is_published',
            'subject_detail', 'teacher_detail', 'lessons_count',
            'enrolled_students_count', 'total_duration',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_subject_detail(self, obj):
        if obj.subject and not obj.subject.deleted:
            return SubjectListingSerializer(obj.subject).data
        return None
    
    def get_teacher_detail(self, obj):
        if obj.teacher and not obj.teacher.deleted:
            return TeacherListSerializer(obj.teacher).data
        return None
    
    def get_lessons_count(self, obj):
        if obj.deleted:
            return 0
        return obj.lessons.filter(deleted=False).count()
    
    def get_enrolled_students_count(self, obj):
        if obj.deleted:
            return 0
        return obj.courseenrollment_set.filter(deleted=False).count()
    
    def get_total_duration(self, obj):
        """Calculate total duration from all lessons"""
        if obj.deleted:
            return 0
        lessons = obj.lessons.filter(deleted=False)
        return sum(lesson.duration_minutes for lesson in lessons)
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Course title must be at least 3 characters long")
        return value.strip()
    
    def validate_subject(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted subject")
        return value
    
    def validate_teacher(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_duration_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        if value > 1000:
            raise serializers.ValidationError("Duration cannot exceed 1000 hours")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Course "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Lesson Serializers ====================

class LessonListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for lesson listings"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'course_title', 'duration_minutes', 
            'order', 'is_preview'
        ]


class LessonSerializer(serializers.ModelSerializer):
    """Full lesson serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    course_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'title', 'content', 'video_url', 
            'video_file', 'duration_minutes', 'order', 'attachments',
            'is_preview', 'course_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_course_detail(self, obj):
        if obj.course and not obj.course.deleted:
            return CourseListingSerializer(obj.course).data
        return None
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Lesson title must be at least 3 characters long")
        return value.strip()
    
    def validate_course(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted course")
        return value
    
    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        if value > 600:  # 10 hours max
            raise serializers.ValidationError("Duration cannot exceed 600 minutes (10 hours)")
        return value
    
    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("Order must be a positive number")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        video_url = data.get('video_url', getattr(self.instance, 'video_url', None))
        video_file = data.get('video_file', getattr(self.instance, 'video_file', None))
        
        # At least one video source should be provided
        if not video_url and not video_file:
            raise serializers.ValidationError(
                "Either video URL or video file must be provided"
            )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Lesson "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Course Enrollment Serializers ====================

class CourseEnrollmentListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for enrollment listings"""
    student_name = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student_name', 'course_title', 'progress_percentage',
            'enrolled_at', 'certificate_issued'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Full enrollment serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    course_detail = serializers.SerializerMethodField()
    completed_lessons_count = serializers.SerializerMethodField()
    total_lessons_count = serializers.SerializerMethodField()
    time_spent_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'course', 'enrolled_at', 'progress_percentage',
            'completed_at', 'certificate_issued',
            'student_detail', 'course_detail', 'completed_lessons_count',
            'total_lessons_count', 'time_spent_hours',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'enrolled_at', 'created_at', 
            'updated_at', 'created_by', 'updated_by'
        )
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListSerializer(obj.student).data
        return None
    
    def get_course_detail(self, obj):
        if obj.course and not obj.course.deleted:
            return CourseListingSerializer(obj.course).data
        return None
    
    def get_completed_lessons_count(self, obj):
        if obj.deleted:
            return 0
        return obj.lessonprogress_set.filter(
            deleted=False, 
            is_completed=True
        ).count()
    
    def get_total_lessons_count(self, obj):
        if obj.deleted or obj.course.deleted:
            return 0
        return obj.course.lessons.filter(deleted=False).count()
    
    def get_time_spent_hours(self, obj):
        """Calculate total time spent in hours"""
        if obj.deleted:
            return 0
        total_minutes = sum(
            progress.time_spent_minutes 
            for progress in obj.lessonprogress_set.filter(deleted=False)
        )
        return round(total_minutes / 60, 2)
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot enroll a deleted student")
        return value
    
    def validate_course(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot enroll in a deleted course")
        if not value.is_published:
            raise serializers.ValidationError("Cannot enroll in an unpublished course")
        return value
    
    def validate(self, data):
        """Check for duplicate enrollment"""
        student = data.get('student', getattr(self.instance, 'student', None))
        course = data.get('course', getattr(self.instance, 'course', None))
        
        if student and course:
            qs = CourseEnrollment.objects.filter(
                student=student,
                course=course,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    "Student is already enrolled in this course"
                )
        
        return data
    
    def validate_progress_percentage(self, value):
        """Validate progress percentage is between 0 and 100"""
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Progress percentage must be between 0 and 100"
            )
        return value
    
    def update(self, instance, validated_data):
        """Custom update to handle progress-related logic"""
        # Update completion status based on progress
        progress = validated_data.get('progress_percentage', instance.progress_percentage)
        
        if progress == 100 and not instance.completed_at:
            validated_data['completed_at'] = timezone.now()
            validated_data['certificate_issued'] = True
        elif progress < 100 and instance.completed_at:
            # Reset completion if progress goes below 100%
            validated_data['completed_at'] = None
            validated_data['certificate_issued'] = False
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Enrollment has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('enrolled_at'), str):
            data['enrolled_at'] = data['enrolled_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('completed_at'), str):
            data['completed_at'] = data['completed_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Lesson Progress Serializers ====================

class LessonProgressListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for lesson progress listings"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson_title', 'is_completed', 
            'time_spent_minutes', 'last_accessed'
        ]


class LessonProgressSerializer(serializers.ModelSerializer):
    """Full lesson progress serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    enrollment_detail = serializers.SerializerMethodField()
    lesson_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'enrollment', 'lesson', 'is_completed',
            'time_spent_minutes', 'last_accessed', 'completed_at',
            'enrollment_detail', 'lesson_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'last_accessed', 'created_at', 'updated_at', 
            'created_by', 'updated_by'
        )
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_enrollment_detail(self, obj):
        if obj.enrollment and not obj.enrollment.deleted:
            return CourseEnrollmentListingSerializer(obj.enrollment).data
        return None
    
    def get_lesson_detail(self, obj):
        if obj.lesson and not obj.lesson.deleted:
            return LessonListingSerializer(obj.lesson).data
        return None
    
    def validate_enrollment(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted enrollment")
        return value
    
    def validate_lesson(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted lesson")
        return value
    
    def validate_time_spent_minutes(self, value):
        if value < 0:
            raise serializers.ValidationError("Time spent cannot be negative")
        return value
    
    def validate(self, data):
        """Validate lesson belongs to enrollment's course"""
        enrollment = data.get('enrollment', getattr(self.instance, 'enrollment', None))
        lesson = data.get('lesson', getattr(self.instance, 'lesson', None))
        
        if enrollment and lesson:
            if lesson.course_id != enrollment.course_id:
                raise serializers.ValidationError(
                    "Lesson does not belong to the enrolled course"
                )
            
            # Check for duplicate progress record
            qs = LessonProgress.objects.filter(
                enrollment=enrollment,
                lesson=lesson,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    "Progress record already exists for this lesson"
                )
        
        # Auto-set completed_at when marked as completed
        if data.get('is_completed') and not data.get('completed_at'):
            data['completed_at'] = datetime.now()
        
        return data
    
    def update(self, instance, validated_data):
        """Update enrollment progress when lesson is completed"""
        progress = super().update(instance, validated_data)
        
        if validated_data.get('is_completed') and not instance.is_completed:
            # Recalculate enrollment progress
            enrollment = progress.enrollment
            total_lessons = enrollment.course.lessons.filter(deleted=False).count()
            if total_lessons > 0:
                completed_lessons = enrollment.lessonprogress_set.filter(
                    deleted=False,
                    is_completed=True
                ).count()
                enrollment.progress_percentage = (completed_lessons / total_lessons) * 100
                
                # Mark course as completed if all lessons done
                if completed_lessons == total_lessons:
                    enrollment.completed_at = datetime.now()
                    enrollment.certificate_issued = True
                
                enrollment.save()
        
        return progress
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Lesson progress has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('last_accessed'), str):
            data['last_accessed'] = data['last_accessed'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('completed_at'), str):
            data['completed_at'] = data['completed_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Quiz Serializers ====================

class QuizListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for quiz listings"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'subject_name', 'teacher_name',
            'total_marks', 'duration_minutes', 'is_published'
        ]
    
    def get_teacher_name(self, obj):
        if obj.teacher and obj.teacher.user:
            full_name = obj.teacher.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.teacher.user.username
        return None


class QuizSerializer(serializers.ModelSerializer):
    """Full quiz serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    course_detail = serializers.SerializerMethodField()
    lesson_detail = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    teacher_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'lesson', 'subject',
            'teacher', 'duration_minutes', 'total_marks', 'passing_marks',
            'attempts_allowed', 'is_published', 'start_date', 'end_date',
            'course_detail', 'lesson_detail', 'subject_detail', 'teacher_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_course_detail(self, obj):
        if obj.course and not obj.course.deleted:
            return CourseListingSerializer(obj.course).data
        return None
    
    def get_lesson_detail(self, obj):
        if obj.lesson and not obj.lesson.deleted:
            return LessonListingSerializer(obj.lesson).data
        return None
    
    def get_subject_detail(self, obj):
        if obj.subject and not obj.subject.deleted:
            return SubjectListingSerializer(obj.subject).data
        return None
    
    def get_teacher_detail(self, obj):
        if obj.teacher and not obj.teacher.deleted:
            return TeacherListSerializer(obj.teacher).data
        return None
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Quiz title must be at least 3 characters long")
        return value.strip()
    
    def validate_course(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted course")
        return value
    
    def validate_lesson(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted lesson")
        return value
    
    def validate_subject(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted subject")
        return value
    
    def validate_teacher(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        if value > 300:  # 5 hours max
            raise serializers.ValidationError("Duration cannot exceed 300 minutes (5 hours)")
        return value
    
    def validate_total_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total marks must be greater than 0")
        return value
    
    def validate_passing_marks(self, value):
        if value < 0:
            raise serializers.ValidationError("Passing marks cannot be negative")
        return value
    
    def validate_attempts_allowed(self, value):
        if value <= 0:
            raise serializers.ValidationError("Attempts allowed must be at least 1")
        if value > 10:
            raise serializers.ValidationError("Attempts allowed cannot exceed 10")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        total_marks = data.get('total_marks', getattr(self.instance, 'total_marks', None))
        passing_marks = data.get('passing_marks', getattr(self.instance, 'passing_marks', None))
        
        if total_marks and passing_marks:
            if passing_marks > total_marks:
                raise serializers.ValidationError({
                    'passing_marks': 'Passing marks cannot exceed total marks'
                })
        
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        
        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })
        
        # Validate lesson belongs to course if both provided
        course = data.get('course', getattr(self.instance, 'course', None))
        lesson = data.get('lesson', getattr(self.instance, 'lesson', None))
        
        if course and lesson:
            if lesson.course_id != course.id:
                raise serializers.ValidationError({
                    'lesson': 'Lesson does not belong to the selected course'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Quiz "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('start_date'), str):
            data['start_date'] = data['start_date'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('end_date'), str):
            data['end_date'] = data['end_date'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Question Serializers ====================

class QuestionListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for question listings"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    options_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'quiz_title', 'question_text', 'question_type',
            'marks', 'order', 'options_count'
        ]
    
    def get_options_count(self, obj):
        if obj.deleted:
            return 0
        return obj.options.filter(deleted=False).count()


class QuestionSerializer(serializers.ModelSerializer):
    """Full question serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    quiz_detail = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'quiz', 'question_text', 'question_type', 'marks',
            'order', 'image', 'quiz_detail', 'options',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_quiz_detail(self, obj):
        if obj.quiz and not obj.quiz.deleted:
            # Remove this line: from .serializers import QuizListingSerializer
            return QuizListingSerializer(obj.quiz).data
        return None
    
    def get_options(self, obj):
        """Return options only for MCQ and True/False questions"""
        if obj.question_type in ['mcq', 'true_false'] and not obj.deleted:
            options = obj.options.filter(deleted=False)
            return QuestionOptionListingSerializer(options, many=True).data
        return []
    
    def validate_quiz(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted quiz")
        return value
    
    def validate_question_text(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Question text must be at least 5 characters long")
        return value.strip()
    
    def validate_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Marks must be greater than 0")
        if value > 100:
            raise serializers.ValidationError("Marks cannot exceed 100")
        return value
    
    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("Order must be a positive number")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Question has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Question Option Serializers ====================

class QuestionOptionListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for question option listings"""
    
    class Meta:
        model = QuestionOption
        fields = ['id', 'option_text', 'is_correct', 'order']


class QuestionOptionSerializer(serializers.ModelSerializer):
    """Full question option serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    question_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionOption
        fields = [
            'id', 'question', 'option_text', 'is_correct', 'order',
            'question_detail', 'created_by', 'updated_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_question_detail(self, obj):
        if obj.question and not obj.question.deleted:
            return QuestionListingSerializer(obj.question).data
        return None
    
    def validate_question(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted question")
        if value.question_type not in ['mcq', 'true_false']:
            raise serializers.ValidationError(
                "Options can only be added to MCQ or True/False questions"
            )
        return value
    
    def validate_option_text(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Option text cannot be empty")
        return value.strip()
    
    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("Order must be a positive number")
        return value
    
    def validate(self, data):
        """Validate True/False questions have exactly 2 options"""
        question = data.get('question', getattr(self.instance, 'question', None))
        
        if question and question.question_type == 'true_false':
            existing_options = question.options.filter(deleted=False)
            if self.instance:
                existing_options = existing_options.exclude(id=self.instance.id)
            
            if existing_options.count() >= 2:
                raise serializers.ValidationError(
                    "True/False questions can only have 2 options"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Question option has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Quiz Attempt Serializers ====================

class QuizAttemptListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for quiz attempt listings"""
    student_name = serializers.SerializerMethodField()
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student_name', 'quiz_title', 'attempt_number',
            'status', 'marks_obtained', 'percentage', 'start_time'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None



class QuizAttemptSerializer(serializers.ModelSerializer):
    """Full quiz attempt serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    quiz_detail = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    time_taken_minutes = serializers.SerializerMethodField()
    pass_status = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'student', 'attempt_number', 'start_time',
            'end_time', 'status', 'marks_obtained', 'percentage',
            'quiz_detail', 'student_detail', 'answers_count',
            'time_taken_minutes', 'pass_status',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'start_time', 'attempt_number', 'created_at',
            'updated_at', 'created_by', 'updated_by'
        )
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_quiz_detail(self, obj):
        if obj.quiz and not obj.quiz.deleted:
            return QuizListingSerializer(obj.quiz).data
        return None
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListSerializer(obj.student).data
        return None
    
    def get_answers_count(self, obj):
        if obj.deleted:
            return 0
        return obj.answers.filter(deleted=False).count()
    
    def get_time_taken_minutes(self, obj):
        """Calculate time taken in minutes"""
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)
        return None
    
    def get_pass_status(self, obj):
        """Check if student passed the quiz"""
        if obj.status == 'graded' and obj.marks_obtained is not None:
            if obj.marks_obtained >= obj.quiz.passing_marks:
                return 'passed'
            return 'failed'
        return None
    
    def validate_quiz(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot attempt a deleted quiz")
        if not value.is_published:
            raise serializers.ValidationError("Cannot attempt an unpublished quiz")
        return value
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted student")
        return value
    
    def validate_start_time(self, value):
        """Prevent start_time from being set in payload"""
        if value is not None:
            raise serializers.ValidationError("start_time is automatically set and cannot be modified")
        return value
    
    def validate_end_time(self, value):
        """Validate end_time is not in the past and not before start_time"""
        if value is not None:
            # Get start_time from instance or current time
            if self.instance and self.instance.start_time:
                start_time = self.instance.start_time
            else:
                start_time = timezone.now()
            
            # Check if end_time is before start_time
            if value <= start_time:
                raise serializers.ValidationError(
                    "End time must be after start time"
                )
            
            # For new attempts, end_time must be in future
            if not self.instance and value < timezone.now():
                raise serializers.ValidationError(
                    "End time cannot be in the past"
                )
        
        return value
    
    def validate_marks_obtained(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Marks obtained cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        quiz = data.get('quiz', getattr(self.instance, 'quiz', None))
        student = data.get('student', getattr(self.instance, 'student', None))
        marks_obtained = data.get('marks_obtained')
        end_time = data.get('end_time')
        
        # Get start_time from instance or use current time for validation
        if self.instance:
            start_time = self.instance.start_time
        else:
            start_time = timezone.now()
        
        # Validate marks don't exceed total
        if marks_obtained is not None and quiz:
            if marks_obtained > quiz.total_marks:
                raise serializers.ValidationError({
                    'marks_obtained': 'Marks obtained cannot exceed total marks'
                })
        
        # Auto-calculate percentage
        if marks_obtained is not None and quiz:
            data['percentage'] = (marks_obtained / quiz.total_marks) * 100
        
        # Check attempt limit
        if not self.instance and quiz and student:
            existing_attempts = QuizAttempt.objects.filter(
                quiz=quiz,
                student=student,
                deleted=False
            ).count()
            
            if existing_attempts >= quiz.attempts_allowed:
                raise serializers.ValidationError(
                    f"Maximum attempts ({quiz.attempts_allowed}) reached for this quiz"
                )
            
            # Auto-set attempt number
            data['attempt_number'] = existing_attempts + 1
        
        # Validate end_time is after start_time (additional check)
        if end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time'
            })
        
        # Validate status transitions
        if self.instance:
            current_status = self.instance.status
            new_status = data.get('status', current_status)
            
            # Define allowed status transitions
            allowed_transitions = {
                'in_progress': ['submitted', 'in_progress'],
                'submitted': ['graded', 'submitted'],
                'graded': ['graded']  # Cannot go back once graded
            }
            
            if current_status in allowed_transitions:
                if new_status not in allowed_transitions[current_status]:
                    raise serializers.ValidationError({
                        'status': f"Cannot change status from '{current_status}' to '{new_status}'"
                    })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Quiz attempt has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        datetime_fields = ['start_time', 'end_time', 'created_at', 'updated_at']
        for field in datetime_fields:
            if isinstance(data.get(field), str):
                data[field] = data[field].replace('T', ' ').split('.')[0]
        
        return data
    
    def create(self, validated_data):
        """Override create to ensure start_time is set automatically"""
        validated_data['start_time'] = timezone.now()
        
        # Set status to in_progress if not provided
        if 'status' not in validated_data:
            validated_data['status'] = 'in_progress'
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Override update to handle status changes"""
        # If changing status to submitted, auto-set end_time if not provided
        if 'status' in validated_data and validated_data['status'] == 'submitted':
            if 'end_time' not in validated_data and not instance.end_time:
                validated_data['end_time'] = timezone.now()
        
        return super().update(instance, validated_data)
# ==================== Quiz Answer Serializers ====================

class QuizAnswerListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for quiz answer listings"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'question_text', 'is_correct', 'marks_awarded'
        ]


class QuizAnswerSerializer(serializers.ModelSerializer):
    """Full quiz answer serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    attempt_detail = serializers.SerializerMethodField()
    question_detail = serializers.SerializerMethodField()
    selected_option_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'attempt', 'question', 'selected_option', 'text_answer',
            'is_correct', 'marks_awarded',
            'attempt_detail', 'question_detail', 'selected_option_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_attempt_detail(self, obj):
        if obj.attempt and not obj.attempt.deleted:
            return QuizAttemptListingSerializer(obj.attempt).data
        return None
    
    def get_question_detail(self, obj):
        if obj.question and not obj.question.deleted:
            return QuestionListingSerializer(obj.question).data
        return None
    
    def get_selected_option_detail(self, obj):
        if obj.selected_option and not obj.selected_option.deleted:
            return QuestionOptionListingSerializer(obj.selected_option).data
        return None
    
    def validate_attempt(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted quiz attempt")
        if value.status == 'graded':
            raise serializers.ValidationError("Cannot modify answers for a graded attempt")
        return value
    
    def validate_question(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted question")
        return value
    
    def validate_selected_option(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted option")
        return value
    
    def validate_marks_awarded(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Marks awarded cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        question = data.get('question', getattr(self.instance, 'question', None))
        selected_option = data.get('selected_option', getattr(self.instance, 'selected_option', None))
        text_answer = data.get('text_answer', getattr(self.instance, 'text_answer', ''))
        attempt = data.get('attempt', getattr(self.instance, 'attempt', None))
        marks_awarded = data.get('marks_awarded')
        
        # Validate question belongs to the quiz
        if attempt and question:
            if question.quiz_id != attempt.quiz_id:
                raise serializers.ValidationError({
                    'question': 'Question does not belong to the quiz being attempted'
                })
        
        # Validate answer type matches question type
        if question:
            if question.question_type in ['mcq', 'true_false']:
                if not selected_option:
                    raise serializers.ValidationError({
                        'selected_option': f'{question.question_type.upper()} questions require a selected option'
                    })
                # Validate option belongs to question
                if selected_option and selected_option.question_id != question.id:
                    raise serializers.ValidationError({
                        'selected_option': 'Selected option does not belong to this question'
                    })
            
            elif question.question_type in ['short_answer', 'essay']:
                if not text_answer or not text_answer.strip():
                    raise serializers.ValidationError({
                        'text_answer': f'{question.question_type.replace("_", " ").title()} questions require text answer'
                    })
        
        # Validate marks don't exceed question marks
        if marks_awarded is not None and question:
            if marks_awarded > question.marks:
                raise serializers.ValidationError({
                    'marks_awarded': 'Marks awarded cannot exceed question marks'
                })
        
        # Auto-grade MCQ and True/False questions
        if question and question.question_type in ['mcq', 'true_false'] and selected_option:
            data['is_correct'] = selected_option.is_correct
            if selected_option.is_correct:
                data['marks_awarded'] = question.marks
            else:
                data['marks_awarded'] = 0
        
        # Check for duplicate answers
        if not self.instance and attempt and question:
            existing_answer = QuizAnswer.objects.filter(
                attempt=attempt,
                question=question,
                deleted=False
            ).exists()
            
            if existing_answer:
                raise serializers.ValidationError(
                    "Answer already exists for this question in this attempt"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': 'Quiz answer has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data