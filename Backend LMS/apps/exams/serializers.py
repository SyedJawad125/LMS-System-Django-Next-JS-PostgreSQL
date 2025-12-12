import re
from rest_framework import serializers
from .models import ExamType, Exam, ExamSchedule, ExamResult, GradeSystem
from apps.academic.serializers import AcademicYearListingSerializer, ClassListingSerializer, SubjectListingSerializer
from apps.users.serializers import StudentListSerializer, TeacherListSerializer


# ==================== Exam Type Serializers ====================

class ExamTypeListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for exam type listings"""
    
    class Meta:
        model = ExamType
        fields = ['id', 'name', 'code', 'weightage']


class ExamTypeSerializer(serializers.ModelSerializer):
    """Full exam type serializer with validations and auto-generated code"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    exams_count = serializers.SerializerMethodField()
    code = serializers.CharField(read_only=True)  # Make code read-only since it's auto-generated
    
    class Meta:
        model = ExamType
        fields = [
            'id', 'name', 'code', 'weightage', 'description',
            'created_by', 'updated_by', 'created_at', 'updated_at', 'exams_count'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'code')
    
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
    
    def get_exams_count(self, obj):
        if obj.deleted:
            return 0
        return obj.exam_set.filter(deleted=False).count()
    
    def generate_code_from_name(self, name):
        """
        Generate code from name in format: NAME_001
        Example: "Mid Term Exam" -> "MID_TERM_EXAM_001"
        """
        # Clean and format the name
        clean_name = name.strip().upper()
        # Replace spaces and special characters with underscore
        clean_name = re.sub(r'[^A-Z0-9]+', '_', clean_name)
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        # Find existing codes with similar pattern
        base_code = clean_name
        existing_codes = ExamType.objects.filter(
            code__startswith=base_code,
            deleted=False
        ).exclude(
            id=self.instance.id if self.instance else None
        ).values_list('code', flat=True)
        
        if not existing_codes:
            # No existing codes, start with 001
            return f"{base_code}_001"
        
        # Extract sequence numbers from existing codes
        max_sequence = 0
        for code in existing_codes:
            # Try to extract the sequence number from the end
            match = re.search(r'_(\d+)$', code)
            if match:
                seq_num = int(match.group(1))
                max_sequence = max(max_sequence, seq_num)
        
        # Generate next sequence number
        next_sequence = max_sequence + 1
        return f"{base_code}_{next_sequence:03d}"
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Exam type name must be at least 2 characters long")
        
        # Check for duplicate name (case-insensitive)
        qs = ExamType.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Exam type with name '{value}' already exists")
        
        return value.strip()
    
    def validate_weightage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Weightage must be between 0 and 100")
        return value
    
    def create(self, validated_data):
        """Override create to auto-generate code"""
        name = validated_data.get('name')
        
        # Generate code from name
        validated_data['code'] = self.generate_code_from_name(name)
        
        # Set created_by from request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Override update to regenerate code if name changes"""
        name = validated_data.get('name')
        
        # If name is being updated, regenerate code
        if name and name != instance.name:
            validated_data['code'] = self.generate_code_from_name(name)
        
        # Set updated_by from request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Exam type "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format timestamps
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data

# ==================== Exam Serializers ====================

class ExamListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for exam listings"""
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type_name', 'class_name', 'start_date', 'end_date', 'is_published']


class ExamSerializer(serializers.ModelSerializer):
    """Full exam serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    exam_type_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    class_level_detail = serializers.SerializerMethodField()
    schedules_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_type', 'academic_year', 'class_level',
            'start_date', 'end_date', 'is_published', 'description',
            'exam_type_detail', 'academic_year_detail', 'class_level_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at', 'schedules_count'
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
    
    def get_exam_type_detail(self, obj):
        if obj.exam_type and not obj.exam_type.deleted:
            return ExamTypeListingSerializer(obj.exam_type).data
        return None
    
    def get_academic_year_detail(self, obj):
        if obj.academic_year and not obj.academic_year.deleted:
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def get_class_level_detail(self, obj):
        if obj.class_level and not obj.class_level.deleted:
            return ClassListingSerializer(obj.class_level).data
        return None
    
    def get_schedules_count(self, obj):
        if obj.deleted:
            return 0
        return obj.schedules.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Exam name must be at least 3 characters long")
        return value.strip()
    
    def validate_exam_type(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted exam type")
        return value
    
    def validate_academic_year(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted academic year")
        return value
    
    def validate_class_level(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted class")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after or equal to start date'
                })
        
        # Check for duplicate exam
        exam_type = data.get('exam_type', getattr(self.instance, 'exam_type', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        class_level = data.get('class_level', getattr(self.instance, 'class_level', None))
        
        if exam_type and academic_year and class_level:
            qs = Exam.objects.filter(
                exam_type=exam_type,
                academic_year=academic_year,
                class_level=class_level,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"An exam of type '{exam_type.name}' already exists for class '{class_level.name}' in academic year '{academic_year.name}'"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Exam "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Exam Schedule Serializers ====================

class ExamScheduleListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for exam schedule listings"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    
    class Meta:
        model = ExamSchedule
        fields = ['id', 'exam_name', 'subject_name', 'date', 'start_time', 'end_time', 'max_marks']


class ExamScheduleSerializer(serializers.ModelSerializer):
    """Full exam schedule serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    exam_detail = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    results_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamSchedule
        fields = [
            'id', 'exam', 'subject', 'date', 'start_time', 'end_time',
            'room', 'max_marks', 'min_passing_marks',
            'exam_detail', 'subject_detail', 'duration_minutes', 'results_count',
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
    
    def get_exam_detail(self, obj):
        if obj.exam and not obj.exam.deleted:
            return ExamListingSerializer(obj.exam).data
        return None
    
    def get_subject_detail(self, obj):
        if obj.subject and not obj.subject.deleted:
            return SubjectListingSerializer(obj.subject).data
        return None
    
    def get_duration_minutes(self, obj):
        """Calculate duration in minutes"""
        if obj.start_time and obj.end_time:
            from datetime import datetime
            start = datetime.combine(datetime.today(), obj.start_time)
            end = datetime.combine(datetime.today(), obj.end_time)
            duration = end - start
            return int(duration.total_seconds() / 60)
        return 0
    
    def get_results_count(self, obj):
        if obj.deleted:
            return 0
        return obj.examresult_set.filter(deleted=False).count()
    
    def validate_exam(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted exam")
        return value
    
    def validate_subject(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted subject")
        return value
    
    def validate_max_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Maximum marks must be greater than 0")
        return value
    
    def validate_min_passing_marks(self, value):
        if value < 0:
            raise serializers.ValidationError("Minimum passing marks cannot be negative")
        return value
    
    def validate_room(self, value):
        if value and len(value.strip()) < 1:
            raise serializers.ValidationError("Room name cannot be empty if provided")
        return value.strip() if value else ""
    
    def validate(self, data):
        """Cross-field validation"""
        start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = data.get('end_time', getattr(self.instance, 'end_time', None))
        
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time'
                })
        
        # Validate passing marks vs max marks
        max_marks = data.get('max_marks', getattr(self.instance, 'max_marks', None))
        min_passing_marks = data.get('min_passing_marks', getattr(self.instance, 'min_passing_marks', None))
        
        if max_marks and min_passing_marks:
            if min_passing_marks > max_marks:
                raise serializers.ValidationError({
                    'min_passing_marks': 'Minimum passing marks cannot be greater than maximum marks'
                })
        
        # Validate date is within exam period
        exam = data.get('exam', getattr(self.instance, 'exam', None))
        date = data.get('date', getattr(self.instance, 'date', None))
        
        if exam and date:
            if date < exam.start_date or date > exam.end_date:
                raise serializers.ValidationError({
                    'date': f'Exam date must be between {exam.start_date} and {exam.end_date}'
                })
        
        # Check for duplicate schedule
        exam = data.get('exam', getattr(self.instance, 'exam', None))
        subject = data.get('subject', getattr(self.instance, 'subject', None))
        
        if exam and subject:
            qs = ExamSchedule.objects.filter(exam=exam, subject=subject, deleted=False)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"A schedule for subject '{subject.name}' already exists for this exam"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'exam': instance.exam.name if instance.exam else None,
                'subject': instance.subject.name if instance.subject else None,
                'message': f'Exam schedule has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Exam Result Serializers ====================

class ExamResultListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for exam result listings"""
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='exam_schedule.subject.name', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = ['id', 'student_name', 'subject_name', 'marks_obtained', 'grade', 'is_absent']
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class ExamResultSerializer(serializers.ModelSerializer):
    """Full exam result serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    exam_schedule_detail = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    entered_by_detail = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamResult
        fields = [
            'id', 'exam_schedule', 'student', 'marks_obtained', 'grade',
            'remarks', 'is_absent', 'entered_by', 'entered_at',
            'exam_schedule_detail', 'student_detail', 'entered_by_detail',
            'percentage', 'status',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('entered_at', 'grade', 'created_at', 'updated_at', 'created_by', 'updated_by')
         # ADD THIS:
        extra_kwargs = {
            'exam_schedule': {'required': True},
            'student': {'required': True}
        }
    
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
    
    def get_exam_schedule_detail(self, obj):
        if obj.exam_schedule and not obj.exam_schedule.deleted:
            return ExamScheduleListingSerializer(obj.exam_schedule).data
        return None
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            return StudentListSerializer(obj.student).data
        return None
    
    def get_entered_by_detail(self, obj):
        if obj.entered_by and not obj.entered_by.deleted:
            return TeacherListSerializer(obj.entered_by).data
        return None
    
    def get_percentage(self, obj):
        if obj.is_absent:
            return 0
        if obj.exam_schedule.max_marks > 0:
            return round((float(obj.marks_obtained) / obj.exam_schedule.max_marks) * 100, 2)
        return 0
    
    def get_status(self, obj):
        if obj.is_absent:
            return 'Absent'
        if obj.marks_obtained >= obj.exam_schedule.min_passing_marks:
            return 'Pass'
        return 'Fail'
    
    def validate_exam_schedule(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted exam schedule")
        return value
    
    def validate_student(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot add result for a deleted student")
        return value
    
    def validate_entered_by(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted teacher")
        return value
    
    def validate_marks_obtained(self, value):
        if value < 0:
            raise serializers.ValidationError("Marks cannot be negative")
        return value
    
    def validate(self, data):
        """Professional cross-field validation with proper duplicate handling"""
        instance = getattr(self, 'instance', None)
        
        # Get current values from instance (for updates)
        current_exam_schedule = getattr(instance, 'exam_schedule', None) if instance else None
        current_student = getattr(instance, 'student', None) if instance else None
        current_marks = getattr(instance, 'marks_obtained', None) if instance else None
        current_absent = getattr(instance, 'is_absent', False) if instance else False
        
        # Get new values from data
        exam_schedule = data.get('exam_schedule', current_exam_schedule)
        student = data.get('student', current_student)
        marks_obtained = data.get('marks_obtained', current_marks)
        is_absent = data.get('is_absent', current_absent)
        
        print(f"🔍 DEBUG: Operation = {'UPDATE' if instance else 'CREATE'}")
        print(f"🔍 DEBUG: Instance ID = {getattr(instance, 'id', 'None')}")
        print(f"🔍 DEBUG: Exam Schedule = {exam_schedule.id if exam_schedule else 'None'}")
        print(f"🔍 DEBUG: Student = {student.id if student else 'None'}")

        # 1. Validate required fields for creation
        if not instance:  # CREATE operation
            if not exam_schedule:
                raise serializers.ValidationError({
                    'exam_schedule': 'Exam schedule is required'
                })
            if not student:
                raise serializers.ValidationError({
                    'student': 'Student is required'
                })

        # 2. Validate exam_schedule exists and is not deleted
        if exam_schedule and exam_schedule.deleted:
            raise serializers.ValidationError({
                'exam_schedule': 'Cannot use a deleted exam schedule'
            })

        # 3. Validate marks for absent students
        if is_absent:
            if marks_obtained is not None and marks_obtained > 0:
                raise serializers.ValidationError({
                    'marks_obtained': 'Marks must be 0 for absent students'
                })
            # Auto-set marks to 0 if absent
            data['marks_obtained'] = 0
        else:
            # 4. Validate marks for present students
            if marks_obtained is None:
                raise serializers.ValidationError({
                    'marks_obtained': 'Marks are required for present students'
                })
            
            if marks_obtained < 0:
                raise serializers.ValidationError({
                    'marks_obtained': 'Marks cannot be negative'
                })
            
            # 5. Validate marks against max marks
            if exam_schedule and marks_obtained > exam_schedule.max_marks:
                raise serializers.ValidationError({
                    'marks_obtained': f'Marks cannot exceed maximum marks ({exam_schedule.max_marks})'
                })

        # 6. ENHANCED DUPLICATE VALIDATION
        if exam_schedule and student:
            # Validate student is not deleted
            if student.deleted:
                raise serializers.ValidationError({
                    'student': 'Cannot add result for a deleted student'
                })
            
            # Check if we're actually changing the unique combination
            is_changing_combination = (
                (data.get('exam_schedule') is not None and data.get('exam_schedule') != current_exam_schedule) or
                (data.get('student') is not None and data.get('student') != current_student)
            )
            
            # Only check for duplicates if:
            # - It's a CREATE operation, OR
            # - It's an UPDATE and we're changing the unique combination
            if not instance or is_changing_combination:
                qs = ExamResult.objects.filter(
                    exam_schedule=exam_schedule, 
                    student=student, 
                    deleted=False
                )
                
                if instance and instance.id:
                    qs = qs.exclude(id=instance.id)
                
                duplicate_count = qs.count()
                print(f"🔍 DEBUG: Duplicate check - Found {duplicate_count} existing records")
                
                if qs.exists():
                    existing_result = qs.first()
                    student_name = student.user.get_full_name() if student.user else f"Student ID: {student.id}"
                    
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Result for student '{student_name}' already exists for this exam schedule (Existing ID: {existing_result.id})"
                        ]
                    })
        
        print("✅ DEBUG: Validation passed successfully")
        return data
    
    def create(self, validated_data):
        # Auto-calculate grade based on percentage
        result = super().create(validated_data)
        result.grade = self._calculate_grade(result)
        result.save()
        return result
    
    def update(self, instance, validated_data):
        result = super().update(instance, validated_data)
        result.grade = self._calculate_grade(result)
        result.save()
        return result
    
    def _calculate_grade(self, result):
        """Calculate grade based on percentage with better fallback"""
        if result.is_absent:
            return 'AB'
        
        if result.exam_schedule.max_marks <= 0:
            return 'N/A'
        
        percentage = (float(result.marks_obtained) / result.exam_schedule.max_marks) * 100
        
        try:
            grade_system = GradeSystem.objects.filter(
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                deleted=False
            ).first()
            
            if grade_system:
                return grade_system.grade
        except Exception:
            # Log the error for debugging
            pass
        
        # Fallback grade calculation if GradeSystem is not available
        return self._fallback_grade_calculation(percentage)

    def _fallback_grade_calculation(self, percentage):
        """Fallback grade calculation if GradeSystem is not configured"""
        if percentage >= 90: return 'A+'
        elif percentage >= 80: return 'A'
        elif percentage >= 70: return 'B'
        elif percentage >= 60: return 'C'
        elif percentage >= 50: return 'D'
        elif percentage >= 40: return 'E'
        else: return 'F'
    
    def to_representation(self, instance):
        if instance.deleted:
            student_name = None
            if instance.student and instance.student.user:
                student_name = instance.student.user.get_full_name() or instance.student.user.username
            
            return {
                'id': instance.id,
                'student': student_name,
                'message': f'Exam result has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('entered_at'), str):
            data['entered_at'] = data['entered_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Grade System Serializers ====================

class GradeSystemListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for grade system listings"""
    
    class Meta:
        model = GradeSystem
        fields = ['id', 'name', 'grade', 'min_percentage', 'max_percentage', 'grade_point']


class GradeSystemSerializer(serializers.ModelSerializer):
    """Full grade system serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    percentage_range = serializers.SerializerMethodField()
    
    class Meta:
        model = GradeSystem
        fields = [
            'id', 'name', 'min_percentage', 'max_percentage',
            'grade', 'grade_point', 'description', 'percentage_range',
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
    
    def get_percentage_range(self, obj):
        return f"{obj.min_percentage}% - {obj.max_percentage}%"
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Grade system name must be at least 2 characters long")
        return value.strip()
    
    def validate_grade(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Grade cannot be empty")
        return value.strip().upper()
    
    def validate_min_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Minimum percentage must be between 0 and 100")
        return value
    
    def validate_max_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Maximum percentage must be between 0 and 100")
        return value
    
    def validate_grade_point(self, value):
        if value < 0:
            raise serializers.ValidationError("Grade point cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        min_percentage = data.get('min_percentage', getattr(self.instance, 'min_percentage', None))
        max_percentage = data.get('max_percentage', getattr(self.instance, 'max_percentage', None))
        
        if min_percentage is not None and max_percentage is not None:
            if max_percentage <= min_percentage:
                raise serializers.ValidationError({
                    'max_percentage': 'Maximum percentage must be greater than minimum percentage'
                })
        
        # Check for overlapping grade ranges
        min_pct = data.get('min_percentage', getattr(self.instance, 'min_percentage', None))
        max_pct = data.get('max_percentage', getattr(self.instance, 'max_percentage', None))
        
        if min_pct is not None and max_pct is not None:
            qs = GradeSystem.objects.filter(
                min_percentage__lt=max_pct,
                max_percentage__gt=min_pct,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                overlapping = qs.first()
                raise serializers.ValidationError(
                    f"Grade range overlaps with existing grade '{overlapping.grade}' ({overlapping.min_percentage}% - {overlapping.max_percentage}%)"
                )
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'grade': instance.grade,
                'message': f'Grade system "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data