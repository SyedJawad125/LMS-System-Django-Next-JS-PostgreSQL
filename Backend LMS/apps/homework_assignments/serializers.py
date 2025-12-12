from rest_framework import serializers
from django.utils import timezone

from utils.enums import *
from .models import Assignment, AssignmentSubmission
from apps.academic.serializers import ClassListingSerializer, SectionListingSerializer, SubjectListingSerializer
from apps.users.serializers import StudentListSerializer, TeacherListSerializer


# ==================== Assignment Serializers ====================

class AssignmentListSerializer(serializers.ModelSerializer):
    """Minimal serializer for assignment listings"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'subject_name', 'class_name', 'section_name',
            'teacher_name', 'assign_date', 'due_date', 'max_marks', 'submissions_count'
        ]
    
    def get_teacher_name(self, obj):
        if obj.teacher and obj.teacher.user:
            full_name = obj.teacher.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.teacher.user.username
        return None
    
    def get_submissions_count(self, obj):
        if obj.deleted:
            return 0
        return obj.submissions.filter(deleted=False).count()


class AssignmentSerializer(serializers.ModelSerializer):
    """Full assignment serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    class_level_detail = serializers.SerializerMethodField()
    section_detail = serializers.SerializerMethodField()
    teacher_detail = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()
    graded_count = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'subject', 'class_level', 'section',
            'teacher', 'assign_date', 'due_date', 'max_marks', 'attachment',
            'instructions', 'subject_detail', 'class_level_detail', 'section_detail',
            'teacher_detail', 'submissions_count', 'graded_count', 'pending_count',
            'has_attachment', 'created_by', 'updated_by', 'created_at', 'updated_at'
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
    
    def get_class_level_detail(self, obj):
        if obj.class_level and not obj.class_level.deleted:
            return ClassListingSerializer(obj.class_level).data
        return None
    
    def get_section_detail(self, obj):
        if obj.section and not obj.section.deleted:
            return SectionListingSerializer(obj.section).data
        return None
    
    def get_teacher_detail(self, obj):
        if obj.teacher and not obj.teacher.deleted:
            return TeacherListSerializer(obj.teacher).data
        return None
    
    def get_submissions_count(self, obj):
        if obj.deleted:
            return 0
        return obj.submissions.filter(deleted=False).count()
    
    def get_graded_count(self, obj):
        if obj.deleted:
            return 0
        return obj.submissions.filter(deleted=False, status=GRADED).count()
    
    def get_pending_count(self, obj):
        if obj.deleted:
            return 0
        return obj.submissions.filter(deleted=False, status__in=[PENDING, SUBMITTED]).count()
    
    def get_has_attachment(self, obj):
        return bool(obj.attachment)
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Assignment title must be at least 3 characters long")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Assignment description must be at least 10 characters long")
        return value.strip()
    
    def validate_subject(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted subject")
        return value
    
    def validate_class_level(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted class")
        return value
    
    def validate_section(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted section")
        return value
    
    def validate_teacher(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_max_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Maximum marks must be greater than 0")
        if value > 1000:
            raise serializers.ValidationError("Maximum marks cannot exceed 1000")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        assign_date = data.get('assign_date', getattr(self.instance, 'assign_date', None))
        due_date = data.get('due_date', getattr(self.instance, 'due_date', None))
        
        if assign_date and due_date:
            if due_date < assign_date:
                raise serializers.ValidationError({
                    'due_date': 'Due date must be on or after assignment date'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Assignment "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Assignment Submission Serializers ====================

class AssignmentSubmissionListSerializer(serializers.ModelSerializer):
    """Minimal serializer for assignment submission listings"""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_name = serializers.SerializerMethodField()
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment_title', 'student_name', 'student_roll',
            'submission_date', 'status', 'marks_obtained'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """Full assignment submission serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    assignment_detail = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    graded_by_detail = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    percentage_score = serializers.SerializerMethodField()
    has_submission_file = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'student', 'submission_file', 'submission_text',
            'submission_date', 'status', 'marks_obtained', 'feedback',
            'graded_by', 'graded_at', 'assignment_detail', 'student_detail',
            'graded_by_detail', 'is_late', 'percentage_score', 'has_submission_file',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('submission_date', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
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
    
    def get_assignment_detail(self, obj):
        if obj.assignment and not obj.assignment.deleted:
            return AssignmentListSerializer(obj.assignment).data
        return None
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListSerializer(obj.student).data
        return None
    
    def get_graded_by_detail(self, obj):
        if obj.graded_by and not obj.graded_by.deleted:
            return TeacherListSerializer(obj.graded_by).data
        return None
    
    def get_is_late(self, obj):
        """Check if submission was late"""
        if obj.assignment and obj.submission_date:
            return obj.submission_date.date() > obj.assignment.due_date
        return False
    
    def get_percentage_score(self, obj):
        """Calculate percentage score"""
        if obj.marks_obtained is not None and obj.assignment:
            return round((float(obj.marks_obtained) / obj.assignment.max_marks) * 100, 2)
        return None
    
    def get_has_submission_file(self, obj):
        return bool(obj.submission_file)
    
    def validate_assignment(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot submit to a deleted assignment")
        return value
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot create submission for a deleted student")
        return value
    
    def validate_graded_by(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_marks_obtained(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Marks obtained cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        assignment = data.get('assignment', getattr(self.instance, 'assignment', None))
        marks_obtained = data.get('marks_obtained', getattr(self.instance, 'marks_obtained', None))
        status = data.get('status', getattr(self.instance, 'status', None))
        graded_by = data.get('graded_by', getattr(self.instance, 'graded_by', None))
        
        # Validate marks don't exceed maximum
        if marks_obtained is not None and assignment:
            if marks_obtained > assignment.max_marks:
                raise serializers.ValidationError({
                    'marks_obtained': f'Marks obtained cannot exceed maximum marks ({assignment.max_marks})'
                })
        
        # Auto-set graded_at when status is graded
        if status == GRADED and not data.get('graded_at'):
            data['graded_at'] = timezone.now()
        
        # Validate graded_by is set when status is graded
        if status == GRADED and not graded_by and not getattr(self.instance, 'graded_by', None):
            raise serializers.ValidationError({
                'graded_by': 'Graded by teacher must be specified when status is graded'
            })
        
        # Check if submission is late
        if assignment and not self.instance:
            from datetime import date
            if date.today() > assignment.due_date:
                data['status'] = LATE_SUBMISSION
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'assignment': instance.assignment_id,
                'student': instance.student_id,
                'message': 'Assignment submission has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('submission_date'), str):
            data['submission_date'] = data['submission_date'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('graded_at'), str) and data.get('graded_at'):
            data['graded_at'] = data['graded_at'].replace('T', ' ').split('.')[0]
        
        return data