from datetime import date
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import ReportCard, StudentBehavior
from apps.academic.serializers import AcademicYearListingSerializer
from apps.exams.serializers import ExamListingSerializer
from apps.users.serializers import StudentListSerializer, TeacherListSerializer


# ==================== Report Card Serializers ====================

class ReportCardListSerializer(serializers.ModelSerializer):
    """Minimal serializer for report card listings"""
    student_name = serializers.SerializerMethodField()
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    
    class Meta:
        model = ReportCard
        fields = [
            'id', 'student_name', 'exam_name', 'marks_obtained', 
            'total_marks', 'percentage', 'grade', 'rank_in_class'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class ReportCardSerializer(serializers.ModelSerializer):
    """Full report card serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    exam_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportCard
        fields = [
            'id', 'student', 'exam', 'academic_year', 'total_marks',
            'marks_obtained', 'percentage', 'grade', 'rank_in_class',
            'attendance_percentage', 'remarks', 'generated_at',
            'student_detail', 'exam_detail', 'academic_year_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'percentage', 'generated_at', 'created_at', 'updated_at', 
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
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListSerializer(obj.student).data
        return None
    
    def get_exam_detail(self, obj):
        if obj.exam and not obj.exam.deleted:
            return ExamListingSerializer(obj.exam).data
        return None
    
    def get_academic_year_detail(self, obj):
        if obj.academic_year and not obj.academic_year.deleted:
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot create report card for a deleted student")
        return value
    
    def validate_exam(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted exam")
        return value
    
    def validate_academic_year(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted academic year")
        return value
    
    def validate_total_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total marks must be greater than 0")
        return value
    
    def validate_marks_obtained(self, value):
        if value < 0:
            raise serializers.ValidationError("Marks obtained cannot be negative")
        return value
    
    def validate_attendance_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Attendance percentage must be between 0 and 100")
        return value
    
    def validate_rank_in_class(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Rank must be at least 1")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        total_marks = data.get('total_marks', getattr(self.instance, 'total_marks', None))
        marks_obtained = data.get('marks_obtained', getattr(self.instance, 'marks_obtained', None))
        
        # Validate marks obtained doesn't exceed total marks
        if total_marks and marks_obtained and marks_obtained > total_marks:
            raise serializers.ValidationError({
                'marks_obtained': 'Marks obtained cannot exceed total marks'
            })
        
        # Auto-calculate percentage
        if total_marks and marks_obtained is not None:
            data['percentage'] = round((marks_obtained / total_marks) * 100, 2)
        
        return data
    
    def create(self, validated_data):
        """Ensure percentage is calculated on creation"""
        if 'percentage' not in validated_data:
            total = validated_data.get('total_marks', 0)
            obtained = validated_data.get('marks_obtained', 0)
            if total > 0:
                validated_data['percentage'] = round((obtained / total) * 100, 2)
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        if instance.deleted:
            student_name = "Unknown Student"
            if instance.student and instance.student.user:
                full_name = instance.student.user.get_full_name()
                student_name = full_name.strip() if full_name and full_name.strip() else instance.student.user.username
            
            return {
                'id': instance.id,
                'student': instance.student_id,
                'exam': instance.exam_id,
                'message': f'Report card for {student_name} has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('generated_at'), str):
            data['generated_at'] = data['generated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Student Behavior Serializers ====================

class StudentBehaviorListSerializer(serializers.ModelSerializer):
    """Minimal serializer for student behavior listings"""
    student_name = serializers.SerializerMethodField()
    reported_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentBehavior
        fields = [
            'id', 'student_name', 'behavior_type', 'title', 
            'incident_date', 'reported_by_name', 'points'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None
    
    def get_reported_by_name(self, obj):
        if obj.reported_by and obj.reported_by.user:
            full_name = obj.reported_by.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.reported_by.user.username
        return None


class StudentBehaviorSerializer(serializers.ModelSerializer):
    """Full student behavior serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    reported_by_detail = serializers.SerializerMethodField()
    behavior_status = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentBehavior
        fields = [
            'id', 'student', 'behavior_type', 'title', 'description',
            'incident_date', 'reported_by', 'action_taken', 'points',
            'student_detail', 'reported_by_detail', 'behavior_status',
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
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListSerializer(obj.student).data
        return None
    
    def get_reported_by_detail(self, obj):
        if obj.reported_by and not obj.reported_by.deleted:
            return TeacherListSerializer(obj.reported_by).data
        return None
    
    def get_behavior_status(self, obj):
        """Get human-readable status based on behavior type and points"""
        if obj.behavior_type == 'positive':
            if obj.points >= 10:
                return 'Excellent'
            elif obj.points >= 5:
                return 'Good'
            else:
                return 'Fair'
        elif obj.behavior_type == 'negative':
            if obj.points <= -10:
                return 'Critical'
            elif obj.points <= -5:
                return 'Concerning'
            else:
                return 'Minor'
        return 'Neutral'
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot create behavior record for a deleted student")
        return value
    
    def validate_reported_by(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot assign a deleted teacher")
        return value
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long")
        return value.strip()
    
    def validate_incident_date(self, value):
        """Validate incident date is not in the future"""
        if value > date.today():
            raise serializers.ValidationError("Incident date cannot be in the future")
        return value
    
    def validate_points(self, value):
        """Validate points based on behavior type"""
        behavior_type = self.initial_data.get('behavior_type')
        
        if behavior_type == 'positive' and value < 0:
            raise serializers.ValidationError("Points must be positive for positive behavior")
        elif behavior_type == 'negative' and value > 0:
            raise serializers.ValidationError("Points must be negative for negative behavior")
        elif behavior_type == 'neutral' and value != 0:
            raise serializers.ValidationError("Points must be zero for neutral behavior")
        
        # Validate points range
        if value < -100 or value > 100:
            raise serializers.ValidationError("Points must be between -100 and 100")
        
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        behavior_type = data.get('behavior_type', getattr(self.instance, 'behavior_type', None))
        points = data.get('points', getattr(self.instance, 'points', None))
        
        # Validate points consistency with behavior type
        if behavior_type and points is not None:
            if behavior_type == 'positive' and points < 0:
                raise serializers.ValidationError({
                    'points': 'Points must be positive for positive behavior'
                })
            elif behavior_type == 'negative' and points > 0:
                raise serializers.ValidationError({
                    'points': 'Points must be negative for negative behavior'
                })
            elif behavior_type == 'neutral' and points != 0:
                raise serializers.ValidationError({
                    'points': 'Points must be zero for neutral behavior'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            student_name = "Unknown Student"
            if instance.student and instance.student.user:
                full_name = instance.student.user.get_full_name()
                student_name = full_name.strip() if full_name and full_name.strip() else instance.student.user.username
            
            return {
                'id': instance.id,
                'student': instance.student_id,
                'title': instance.title,
                'message': f'Behavior record "{instance.title}" for {student_name} has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        # Add additional calculated fields
        data['days_since_incident'] = self.get_days_since_incident(instance)
        
        return data
    
    def get_days_since_incident(self, instance):
        """Calculate days since the incident occurred"""
        if instance.incident_date:
            delta = date.today() - instance.incident_date
            return delta.days
        return None