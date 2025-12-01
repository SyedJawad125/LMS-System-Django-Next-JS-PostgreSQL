from rest_framework import serializers
from .models import TimeSlot, Timetable
from apps.academic.serializers import SectionListingSerializer, SubjectListingSerializer
from apps.users.serializers import TeacherListSerializer


# ==================== TimeSlot Serializers ====================

class TimeSlotListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for time slot listings"""
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'name', 'start_time', 'end_time', 'is_break', 'order']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Full time slot serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    timetables_count = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'name', 'start_time', 'end_time', 'is_break', 'order',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'timetables_count', 'duration_minutes'
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
    
    def get_timetables_count(self, obj):
        if obj.deleted:
            return 0
        return obj.timetable_set.filter(deleted=False).count()
    
    def get_duration_minutes(self, obj):
        """Calculate duration in minutes"""
        if obj.start_time and obj.end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(datetime.today(), obj.start_time)
            end = datetime.combine(datetime.today(), obj.end_time)
            duration = end - start
            return int(duration.total_seconds() / 60)
        return 0
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Time slot name must be at least 2 characters long")
        
        qs = TimeSlot.objects.filter(name__iexact=value.strip(), deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError(f"Time slot with name '{value}' already exists")
        
        return value.strip()
    
    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("Order cannot be negative")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = data.get('end_time', getattr(self.instance, 'end_time', None))
        
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time'
                })
            
            # Check for overlapping time slots
            from datetime import datetime, timedelta
            start = datetime.combine(datetime.today(), start_time)
            end = datetime.combine(datetime.today(), end_time)
            
            overlapping_qs = TimeSlot.objects.filter(deleted=False)
            if self.instance:
                overlapping_qs = overlapping_qs.exclude(id=self.instance.id)
            
            for slot in overlapping_qs:
                slot_start = datetime.combine(datetime.today(), slot.start_time)
                slot_end = datetime.combine(datetime.today(), slot.end_time)
                
                # Check if times overlap
                if (start < slot_end and end > slot_start):
                    raise serializers.ValidationError({
                        'start_time': f'Time slot overlaps with "{slot.name}" ({slot.start_time} - {slot.end_time})'
                    })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Time slot "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Timetable Serializers ====================

class TimetableListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for timetable listings"""
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    time_slot_name = serializers.CharField(source='time_slot.name', read_only=True)
    
    class Meta:
        model = Timetable
        fields = [
            'id', 'section_name', 'day', 'time_slot_name', 
            'subject_name', 'teacher_name', 'room'
        ]
    
    def get_teacher_name(self, obj):
        if obj.teacher and obj.teacher.user:
            return obj.teacher.user.get_full_name() or obj.teacher.user.username
        return None


class TimetableSerializer(serializers.ModelSerializer):
    """Full timetable serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    section_detail = serializers.SerializerMethodField()
    time_slot_detail = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    teacher_detail = serializers.SerializerMethodField()
    academic_year_detail = serializers.SerializerMethodField()
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    class Meta:
        model = Timetable
        fields = [
            'id', 'section', 'section_detail', 'day', 'day_display',
            'time_slot', 'time_slot_detail', 'subject', 'subject_detail',
            'teacher', 'teacher_detail', 'room', 'academic_year', 'academic_year_detail',
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
    
    def get_section_detail(self, obj):
        if obj.section and not obj.section.deleted:
            return SectionListingSerializer(obj.section).data
        return None
    
    def get_time_slot_detail(self, obj):
        if obj.time_slot and not obj.time_slot.deleted:
            return TimeSlotListingSerializer(obj.time_slot).data
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
            from apps.academic.serializers import AcademicYearListingSerializer
            return AcademicYearListingSerializer(obj.academic_year).data
        return None
    
    def validate_section(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot assign timetable to a deleted section")
        return value
    
    def validate_time_slot(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted time slot")
        if value.is_break:
            raise serializers.ValidationError("Cannot assign subject to a break period")
        return value
    
    def validate_subject(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot assign a deleted subject")
        return value
    
    def validate_teacher(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot assign a deleted teacher")
        return value
    
    def validate_academic_year(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted academic year")
        return value
    
    def validate_room(self, value):
        if value and len(value.strip()) < 1:
            raise serializers.ValidationError("Room name cannot be empty if provided")
        return value.strip() if value else ""
    
    def validate(self, data):
        """Cross-field validation"""
        section = data.get('section', getattr(self.instance, 'section', None))
        day = data.get('day', getattr(self.instance, 'day', None))
        time_slot = data.get('time_slot', getattr(self.instance, 'time_slot', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))
        teacher = data.get('teacher', getattr(self.instance, 'teacher', None))
        
        # Check for duplicate timetable entry (handled by unique_together in model)
        if section and day and time_slot and academic_year:
            qs = Timetable.objects.filter(
                section=section,
                day=day,
                time_slot=time_slot,
                academic_year=academic_year,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError({
                    'time_slot': f'This time slot is already assigned for {section.name} on {day}'
                })
        
        # Check teacher availability (no double-booking)
        if teacher and day and time_slot and academic_year:
            teacher_conflicts = Timetable.objects.filter(
                teacher=teacher,
                day=day,
                time_slot=time_slot,
                academic_year=academic_year,
                deleted=False
            )
            if self.instance:
                teacher_conflicts = teacher_conflicts.exclude(id=self.instance.id)
            
            if teacher_conflicts.exists():
                conflict = teacher_conflicts.first()
                raise serializers.ValidationError({
                    'teacher': f'Teacher is already assigned to {conflict.section.name} at this time'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'section': instance.section.name if instance.section else None,
                'day': instance.get_day_display(),
                'message': f'Timetable entry has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data