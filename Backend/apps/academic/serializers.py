from rest_framework import serializers
from django.utils.text import slugify
from .models import AcademicYear, Department, Class, Section, Subject, ClassSubject
from apps.users.serializers import TeacherListSerializer  # Assuming you have this

# ======================= ACADEMIC YEAR SERIALIZERS =======================

class AcademicYearListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for academic year listings in dropdowns"""
    
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'code', 'start_date', 'end_date', 'is_current', 'is_active']


class AcademicYearSerializer(serializers.ModelSerializer):
    """Full academic year serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    sections_count = serializers.SerializerMethodField()
    class_subjects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'name', 'code', 'start_date', 'end_date', 'is_current', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'sections_count', 'class_subjects_count'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        """Get created by user with fallback to username"""
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        """Get updated by user with fallback to username"""
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_sections_count(self, obj):
        """Get sections count"""
        if obj.deleted:
            return 0
        return obj.section_set.filter(deleted=False).count()
    
    def get_class_subjects_count(self, obj):
        """Get class subjects count"""
        if obj.deleted:
            return 0
        return obj.classsubject_set.filter(deleted=False).count()
    
    def validate_name(self, value):
        """Validate academic year name"""
        if len(value.strip()) < 4:
            raise serializers.ValidationError("Academic year name must be at least 4 characters long")
        
        # Check for duplicate names (case-insensitive)
        qs = AcademicYear.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Academic year with name '{value}' already exists")
        
        return value.strip()
    
    def validate_code(self, value):
        """Validate academic year code"""
        if len(value.strip()) < 4:
            raise serializers.ValidationError("Academic year code must be at least 4 characters long")
        
        # Check format (should be like "2024-25")
        import re
        if not re.match(r'^\d{4}-\d{2}$', value.strip()):
            raise serializers.ValidationError("Academic year code must be in format: YYYY-YY (e.g., 2024-25)")
        
        # Check for duplicate codes (case-insensitive)
        qs = AcademicYear.objects.filter(code__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Academic year with code '{value}' already exists")
        
        return value.strip()
    
    def validate_dates(self, start_date, end_date):
        """Validate start and end dates"""
        if start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        
        # Validate code matches dates if both are provided
        if hasattr(self, 'initial_data') and 'code' in self.initial_data:
            code = self.initial_data['code']
            if code and len(code) == 7:  # YYYY-YY format
                code_start_year = code[:4]
                code_end_year = '20' + code[5:]  # Convert YY to YYYY
                
                if (str(start_date.year) != code_start_year or 
                    str(end_date.year) != code_end_year):
                    raise serializers.ValidationError(
                        f"Code {code} doesn't match dates {start_date.year}-{end_date.year}"
                    )
        
        return True
    
    def validate(self, attrs):
        """Cross-field validation"""
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        end_date = attrs.get('end_date', self.instance.end_date if self.instance else None)
        name = attrs.get('name', self.instance.name if self.instance else None)
        code = attrs.get('code', self.instance.code if self.instance else None)
        
        if start_date and end_date:
            self.validate_dates(start_date, end_date)
        
        # Auto-generate code if not provided but name is provided
        if not code and name:
            # Extract code from name (e.g., "2024-2025" -> "2024-25")
            if '-' in name:
                parts = name.split('-')
                if len(parts) >= 2:
                    start_year = parts[0].strip()
                    end_year = parts[1].strip()
                    if len(end_year) == 4:
                        attrs['code'] = f"{start_year}-{end_year[2:]}"
                    else:
                        attrs['code'] = f"{start_year}-{end_year}"
        
        # Auto-generate code from dates if still not available
        if not attrs.get('code') and start_date and end_date:
            attrs['code'] = f"{start_date.year}-{str(end_date.year)[-2:]}"
        
        # If setting as current, unset other current academic years
        if attrs.get('is_current', False):
            AcademicYear.objects.filter(is_current=True, deleted=False).update(is_current=False)
        
        return attrs
    
    def create(self, validated_data):
        """Ensure code is generated before creation"""
        if not validated_data.get('code'):
            # Final fallback - generate from dates
            start_date = validated_data.get('start_date')
            end_date = validated_data.get('end_date')
            if start_date and end_date:
                validated_data['code'] = f"{start_date.year}-{str(end_date.year)[-2:]}"
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Customize output representation"""
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'code': instance.code,
                'message': f'Academic year "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields if needed
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data

# ======================= DEPARTMENT SERIALIZERS =======================

class DepartmentListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for department listings"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head']


class DepartmentSerializer(serializers.ModelSerializer):
    """Full department serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    head_detail = serializers.SerializerMethodField()
    subjects_count = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'head', 'head_detail', 'description',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'subjects_count', 'teachers_count'
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
    
    def get_head_detail(self, obj):
        if obj.head and not obj.head.deleted:
            return TeacherListSerializer(obj.head).data
        return None
    
    def get_subjects_count(self, obj):
        if obj.deleted:
            return 0
        return obj.subject_set.filter(deleted=False).count()
    
    def get_teachers_count(self, obj):
        if obj.deleted:
            return 0
        # Assuming Teacher model has department field
        from apps.users.models import Teacher
        return Teacher.objects.filter(department=obj, deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Department name must be at least 2 characters long")
        
        qs = Department.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Department with name '{value}' already exists")
        
        return value.strip()
    
    def validate_code(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Department code must be at least 2 characters long")
        
        qs = Department.objects.filter(code__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Department with code '{value}' already exists")
        
        return value.strip().upper()
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Department "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data

# ======================= CLASS SERIALIZERS =======================

class ClassListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for class listings"""
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'code', 'level']


class ClassSerializer(serializers.ModelSerializer):
    """Full class serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    sections_count = serializers.SerializerMethodField()
    class_subjects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'code', 'level', 'description',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'sections_count', 'class_subjects_count'
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
    
    def get_sections_count(self, obj):
        if obj.deleted:
            return 0
        return obj.sections.filter(deleted=False).count()
    
    def get_class_subjects_count(self, obj):
        if obj.deleted:
            return 0
        return obj.classsubject_set.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Class name must be at least 2 characters long")
        
        qs = Class.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Class with name '{value}' already exists")
        
        return value.strip()
    
    def validate_code(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Class code must be at least 2 characters long")
        
        qs = Class.objects.filter(code__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Class with code '{value}' already exists")
        
        return value.strip().upper()
    
    def validate_level(self, value):
        if value < 0:
            raise serializers.ValidationError("Level cannot be negative")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Class "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data

# ======================= SECTION SERIALIZERS =======================

class SectionListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for section listings"""
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    class_level_code = serializers.CharField(source='class_level.code', read_only=True)  # Optional
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'class_level', 'class_level_name', 'class_level_code', 'room_number', 'capacity']
        read_only_fields = ['id', 'name', 'class_level', 'class_level_name', 'class_level_code', 'room_number', 'capacity']

class SectionSerializer(serializers.ModelSerializer):
    """Full section serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    class_level_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    class_teacher_detail = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    class_subjects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = [
            'id', 'class_level', 'class_level_detail', 'name', 'academic_year', 'academic_year_detail',
            'class_teacher', 'class_teacher_detail', 'room_number', 'capacity',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'students_count', 'class_subjects_count'
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
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_class_level_detail(self, obj):
        if obj.class_level and not obj.class_level.deleted:
            return ClassListingSerializer(obj.class_level).data
        return None
    
    def get_academic_year_detail(self, obj):
        if obj.academic_year and not obj.academic_year.deleted:
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def get_class_teacher_detail(self, obj):
        if obj.class_teacher and not obj.class_teacher.deleted:
            return TeacherListSerializer(obj.class_teacher).data
        return None
    
    def get_students_count(self, obj):
        if obj.deleted:
            return 0
        # FIXED: Check what field actually links students to sections
        from apps.users.models import Student
        try:
            # Try different possible field names
            if hasattr(Student, 'section'):
                return Student.objects.filter(section=obj, deleted=False).count()
            elif hasattr(Student, 'class_section'):
                return Student.objects.filter(class_section=obj, deleted=False).count()
            elif hasattr(Student, 'student_section'):
                return Student.objects.filter(student_section=obj, deleted=False).count()
            else:
                # If no direct relation, return 0 or implement your logic
                return 0
        except Exception:
            return 0
    
    def get_class_subjects_count(self, obj):
        if obj.deleted:
            return 0
        return obj.classsubject_set.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Section name is required")
        
        value = value.strip().upper()
        
        # Check unique together with class_level and academic_year
        class_level_id = self.initial_data.get('class_level')
        academic_year_id = self.initial_data.get('academic_year')
        
        # For updates, use instance values if initial_data doesn't have them
        if self.instance and not class_level_id:
            class_level_id = self.instance.class_level.id
        if self.instance and not academic_year_id:
            academic_year_id = self.instance.academic_year.id
        
        if class_level_id and academic_year_id:
            qs = Section.objects.filter(
                class_level_id=class_level_id,
                name=value,
                academic_year_id=academic_year_id,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(f"Section with this name already exists for the selected class and academic year")
        
        return value
    
    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1")
        if value > 100:
            raise serializers.ValidationError("Capacity cannot exceed 100")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Section "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data

# ======================= SUBJECT SERIALIZERS =======================

class SubjectListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for subject listings"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'subject_type', 'credit_hours']


class SubjectSerializer(serializers.ModelSerializer):
    """Full subject serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    department_detail = serializers.SerializerMethodField()
    class_subjects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'subject_type', 'department', 'department_detail',
            'credit_hours', 'description',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'class_subjects_count'
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
    
    def get_department_detail(self, obj):
        if obj.department and not obj.department.deleted:
            return DepartmentListingSerializer(obj.department).data
        return None
    
    def get_class_subjects_count(self, obj):
        if obj.deleted:
            return 0
        return obj.classsubject_set.filter(deleted=False).count()
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Subject name must be at least 2 characters long")
        
        qs = Subject.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Subject with name '{value}' already exists")
        
        return value.strip()
    
    def validate_code(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Subject code must be at least 2 characters long")
        
        qs = Subject.objects.filter(code__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Subject with code '{value}' already exists")
        
        return value.strip().upper()
    
    def validate_credit_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("Credit hours cannot be negative")
        if value > 10:
            raise serializers.ValidationError("Credit hours cannot exceed 10")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Subject "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data

# ======================= CLASS SUBJECT SERIALIZERS =======================

class ClassSubjectListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for class subject listings"""
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSubject
        fields = ['id', 'class_level', 'class_level_name', 'subject', 'subject_name', 'teacher', 'teacher_name']
    
    def get_teacher_name(self, obj):
        if obj.teacher and not obj.teacher.deleted:
            return obj.teacher.user.get_full_name()
        return None


class ClassSubjectSerializer(serializers.ModelSerializer):
    """Full class subject serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    class_level_detail = serializers.SerializerMethodField()
    section_detail = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    teacher_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSubject
        fields = [
            'id', 'class_level', 'class_level_detail', 'section', 'section_detail',
            'subject', 'subject_detail', 'teacher', 'teacher_detail',
            'academic_year', 'academic_year_detail',
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
    
    def get_class_level_detail(self, obj):
        if obj.class_level and not obj.class_level.deleted:
            return ClassListingSerializer(obj.class_level).data
        return None
    
    def get_section_detail(self, obj):
        if obj.section and not obj.section.deleted:
            return SectionListingSerializer(obj.section).data
        return None
    
    def get_subject_detail(self, obj):
        if obj.subject and not obj.subject.deleted:
            return SubjectListingSerializer(obj.subject).data
        return None
    
    def get_teacher_detail(self, obj):
        if obj.teacher and not obj.teacher.deleted:
            return TeacherListSerializer(obj.teacher).data
        return None
    
    def get_academic_year_detail(self, obj):
        if obj.academic_year and not obj.academic_year.deleted:
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def validate(self, attrs):
        """Validate unique together constraint"""
        section = attrs.get('section', self.instance.section if self.instance else None)
        subject = attrs.get('subject', self.instance.subject if self.instance else None)
        academic_year = attrs.get('academic_year', self.instance.academic_year if self.instance else None)
        
        if section and subject and academic_year:
            qs = ClassSubject.objects.filter(
                section=section,
                subject=subject,
                academic_year=academic_year,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    "This subject is already assigned to the selected section for this academic year"
                )
        
        return attrs
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'message': f'Class subject assignment has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data