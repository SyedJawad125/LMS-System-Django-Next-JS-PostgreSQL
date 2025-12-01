from decimal import Decimal
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Count, Sum, Q
from .models import (
    DailyAttendance, MonthlyAttendanceReport, 
    AttendanceConfiguration, AttendanceSummary, AttendanceStatus
)
from apps.users.serializers import TeacherListSerializer
from apps.academic.serializers import SectionListingSerializer, SubjectListingSerializer


# ======================= DAILY ATTENDANCE SERIALIZERS =======================

class DailyAttendanceListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for attendance listings"""
    student_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    subject_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyAttendance
        fields = [
            'id', 'student', 'student_name', 'date', 'status', 
            'status_display', 'subject', 'subject_name', 'section', 
            'section_name', 'is_verified'
        ]
    
    def get_student_name(self, obj):
        if obj.student and not obj.student.deleted:
            return obj.student.user.get_full_name()
        return None
    
    def get_subject_name(self, obj):
        if obj.subject and not obj.subject.deleted:
            return obj.subject.name
        return None
    
    def get_section_name(self, obj):
        if obj.section and not obj.section.deleted:
            return obj.section.name
        return None


class DailyAttendanceSerializer(serializers.ModelSerializer):
    """Full daily attendance serializer with validations - AUTO DATE"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    subject_detail = serializers.SerializerMethodField()
    section_detail = serializers.SerializerMethodField()
    marked_by_detail = serializers.SerializerMethodField()
    verified_by_detail = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    attendance_duration_display = serializers.SerializerMethodField()
    is_on_time = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyAttendance
        fields = [
            'id', 'student', 'student_detail', 'date', 'status', 'status_display',  # date is read-only now
            'subject', 'subject_detail', 'section', 'section_detail',
            'marked_by', 'marked_by_detail', 'remarks',
            'check_in_time', 'check_out_time', 'attendance_duration_display',
            'is_verified', 'verified_by', 'verified_by_detail', 'verified_at',
            'is_on_time', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'date', 'created_at', 'updated_at', 'created_by', 'updated_by',  # date added to read_only
            'verified_at', 'attendance_duration_display', 'is_on_time'
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
            from apps.users.serializers import StudentListingSerializer
            return StudentListingSerializer(obj.student).data
        return None
    
    def get_subject_detail(self, obj):
        if obj.subject and not obj.subject.deleted:
            return SubjectListingSerializer(obj.subject).data
        return None
    
    def get_section_detail(self, obj):
        if obj.section and not obj.section.deleted:
            return SectionListingSerializer(obj.section).data
        return None
    
    def get_marked_by_detail(self, obj):
        if obj.marked_by and not obj.marked_by.deleted:
            return TeacherListSerializer(obj.marked_by).data
        return None
    
    def get_verified_by_detail(self, obj):
        if obj.verified_by and not obj.verified_by.deleted:
            return TeacherListSerializer(obj.verified_by).data
        return None
    
    def get_attendance_duration_display(self, obj):
        """Calculate and format attendance duration"""
        if obj.check_in_time and obj.check_out_time:
            check_in_dt = timezone.datetime.combine(obj.date, obj.check_in_time)
            check_out_dt = timezone.datetime.combine(obj.date, obj.check_out_time)
            duration = check_out_dt - check_in_dt
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            return f"{hours}h {minutes}m"
        return None
    
    def get_is_on_time(self, obj):
        """Check if student was on time"""
        if obj.status == AttendanceStatus.LATE and obj.check_in_time:
            try:
                config = AttendanceConfiguration.objects.get(section=obj.section, deleted=False)
                return obj.check_in_time <= config.school_start_time
            except AttendanceConfiguration.DoesNotExist:
                school_start_time = timezone.datetime.strptime('08:00', '%H:%M').time()
                return obj.check_in_time <= school_start_time
        return obj.status != AttendanceStatus.LATE
    
    def validate_status(self, value):
        """Validate status is a valid choice"""
        valid_statuses = [choice[0] for choice in AttendanceStatus.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate_student(self, value):
        """Validate student is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected student has been deleted.")
        return value
    
    def validate_subject(self, value):
        """Validate subject is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected subject has been deleted.")
        return value
    
    def validate_section(self, value):
        """Validate section is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected section has been deleted.")
        return value
    
    def validate_marked_by(self, value):
        """Validate teacher is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected teacher has been deleted.")
        return value
    
    def validate_verified_by(self, value):
        """Validate verified_by teacher is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected verifier has been deleted.")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        status = attrs.get('status', self.instance.status if self.instance else None)
        check_in_time = attrs.get('check_in_time', self.instance.check_in_time if self.instance else None)
        
        # Validate check_in_time is required for late status
        if status == AttendanceStatus.LATE and not check_in_time:
            raise serializers.ValidationError({
                'check_in_time': 'Check-in time is required for late attendance.'
            })
        
        # Validate unique together constraint (exclude soft deleted records)
        student = attrs.get('student', self.instance.student if self.instance else None)
        subject = attrs.get('subject', self.instance.subject if self.instance else None)
        
        if student:
            # Auto-date will be set in create method, so use current date for validation
            current_date = timezone.now().date()
            
            qs = DailyAttendance.objects.filter(
                student=student,
                date=current_date,  # Use current date for validation
                subject=subject,
                deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    "Attendance for this student on today's date and subject already exists."
                )
        
        return attrs
    
    def create(self, validated_data):
        """Auto-populate date and section"""
        # Auto-set current date
        validated_data['date'] = timezone.now().date()
        
        # Auto-populate section from student if not provided
        if 'section' not in validated_data and 'student' in validated_data:
            validated_data['section'] = validated_data['student'].section
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Handle verification status changes"""
        is_verified = validated_data.get('is_verified', instance.is_verified)
        
        if is_verified and not instance.is_verified:
            validated_data['verified_at'] = timezone.now()
        elif not is_verified and instance.is_verified:
            validated_data['verified_at'] = None
            validated_data['verified_by'] = None
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        # Handle soft deleted records
        if instance.deleted:
            return {
                'id': instance.id,
                'student': instance.student_id,
                'date': str(instance.date),
                'message': 'Attendance record has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('verified_at'), str):
            data['verified_at'] = data['verified_at'].replace('T', ' ').split('.')[0]
        
        return data


# ======================= MONTHLY ATTENDANCE REPORT SERIALIZERS =======================

class MonthlyAttendanceReportListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for monthly report listings"""
    student_name = serializers.SerializerMethodField()
    month_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyAttendanceReport
        fields = [
            'id', 'student', 'student_name', 'month', 'year', 
            'month_display', 'attendance_percentage', 'is_finalized'
        ]
    
    def get_student_name(self, obj):
        if obj.student and not obj.student.deleted:
            return obj.student.user.get_full_name()
        return None
    
    def get_month_display(self, obj):
        import calendar
        return f"{calendar.month_name[obj.month]} {obj.year}"




class MonthlyAttendanceReportSerializer(serializers.ModelSerializer):
    """Full monthly attendance report serializer"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    month_display = serializers.SerializerMethodField()
    attendance_breakdown = serializers.SerializerMethodField()
    effective_working_days = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyAttendanceReport
        fields = [
            'id', 'student', 'student_detail', 'month', 'year', 'month_display',
            'total_school_days', 'present_days', 'absent_days', 'late_days',
            'half_days', 'excused_days', 'sick_leave_days',
            'attendance_percentage', 'punctuality_score',
            'previous_month_percentage', 'percentage_change',
            'attendance_breakdown', 'effective_working_days',
            'is_finalized', 'finalized_at',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'created_at', 'updated_at', 'created_by',  # REMOVED 'updated_by' from here
            'attendance_percentage', 'punctuality_score', 'percentage_change',
            'finalized_at'
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
            from apps.users.serializers import StudentListingSerializer
            return StudentListingSerializer(obj.student).data
        return None
    
    def get_month_display(self, obj):
        import calendar
        return f"{calendar.month_name[obj.month]} {obj.year}"
    
    def get_attendance_breakdown(self, obj):
        """Get attendance breakdown as dictionary"""
        return {
            'present': obj.present_days,
            'absent': obj.absent_days,
            'late': obj.late_days,
            'half_day': obj.half_days,
            'excused': obj.excused_days,
            'sick_leave': obj.sick_leave_days,
            'total': obj.total_school_days
        }
    
    def get_effective_working_days(self, obj):
        """Get effective working days excluding excused and sick leaves"""
        return obj.total_school_days - obj.excused_days - obj.sick_leave_days
    
    def validate_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value
    
    def validate_student(self, value):
        """Validate student is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected student has been deleted.")
        return value
    
    def validate(self, attrs):
        """Validate report data"""
        present = attrs.get('present_days', self.instance.present_days if self.instance else 0)
        absent = attrs.get('absent_days', self.instance.absent_days if self.instance else 0)
        late = attrs.get('late_days', self.instance.late_days if self.instance else 0)
        half = attrs.get('half_days', self.instance.half_days if self.instance else 0)
        excused = attrs.get('excused_days', self.instance.excused_days if self.instance else 0)
        sick = attrs.get('sick_leave_days', self.instance.sick_leave_days if self.instance else 0)
        total = attrs.get('total_school_days', self.instance.total_school_days if self.instance else 0)
        
        calculated_total = present + absent + late + half + excused + sick
        
        if calculated_total > total:
            raise serializers.ValidationError(
                "Sum of individual status days cannot exceed total school days."
            )
        
        # Validate unique together (exclude soft deleted)
        student = attrs.get('student', self.instance.student if self.instance else None)
        month = attrs.get('month', self.instance.month if self.instance else None)
        year = attrs.get('year', self.instance.year if self.instance else None)
        
        if student and month and year:
            qs = MonthlyAttendanceReport.objects.filter(
                student=student, month=month, year=year, deleted=False
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            
            if qs.exists():
                raise serializers.ValidationError(
                    "Monthly report for this student already exists for this period."
                )
        
        return attrs
    
    def _calculate_percentage(self, data):
        """Calculate attendance percentage - FIXED VERSION"""
        total = data.get('total_school_days', 0)
        excused = data.get('excused_days', 0)
        sick = data.get('sick_leave_days', 0)
        present = data.get('present_days', 0)
        half = data.get('half_days', 0)
        
        # Convert all to Decimal to avoid type conflicts
        total_dec = Decimal(str(total))
        excused_dec = Decimal(str(excused))
        sick_dec = Decimal(str(sick))
        present_dec = Decimal(str(present))
        half_dec = Decimal(str(half))
        
        if total_dec > 0:
            effective_days = total_dec - excused_dec - sick_dec
            if effective_days > 0:
                # Use Decimal for calculations instead of float
                effective_present = present_dec + (half_dec * Decimal('0.5'))
                percentage = (effective_present / effective_days) * Decimal('100')
                return percentage.quantize(Decimal('0.01'))  # Round to 2 decimal places
        return Decimal('0.00')
    
    def _calculate_punctuality_score(self, data):
        """Calculate punctuality score - FIXED VERSION"""
        present = data.get('present_days', 0)
        late = data.get('late_days', 0)
        half = data.get('half_days', 0)
        
        # Convert all to Decimal
        present_dec = Decimal(str(present))
        late_dec = Decimal(str(late))
        half_dec = Decimal(str(half))
        
        total_attended = present_dec + late_dec + half_dec
        if total_attended > 0:
            # Use Decimal constants instead of float
            score = present_dec + (late_dec * Decimal('0.5')) + (half_dec * Decimal('0.75'))
            punctuality = (score / total_attended) * Decimal('100')
            return punctuality.quantize(Decimal('0.01'))
        return Decimal('0.00')
    
    def create(self, validated_data):
        """Auto-calculate metrics before creating - FIXED VERSION"""
        # Calculate percentages
        validated_data['attendance_percentage'] = self._calculate_percentage(validated_data)
        validated_data['punctuality_score'] = self._calculate_punctuality_score(validated_data)
        
        # Handle percentage change - ensure both are Decimal
        prev_percentage = validated_data.get('previous_month_percentage', Decimal('0'))
        if isinstance(prev_percentage, float):
            prev_percentage = Decimal(str(prev_percentage))
            
        if prev_percentage > 0:
            validated_data['percentage_change'] = (
                validated_data['attendance_percentage'] - prev_percentage
            )
        else:
            validated_data['percentage_change'] = Decimal('0.00')
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Handle finalization and recalculate metrics - FIXED to set updated_by"""
        # Merge with existing values for calculation
        calc_data = {
            'total_school_days': validated_data.get('total_school_days', instance.total_school_days),
            'present_days': validated_data.get('present_days', instance.present_days),
            'absent_days': validated_data.get('absent_days', instance.absent_days),
            'late_days': validated_data.get('late_days', instance.late_days),
            'half_days': validated_data.get('half_days', instance.half_days),
            'excused_days': validated_data.get('excused_days', instance.excused_days),
            'sick_leave_days': validated_data.get('sick_leave_days', instance.sick_leave_days),
            'previous_month_percentage': validated_data.get('previous_month_percentage', instance.previous_month_percentage),
        }
        
        # Calculate percentages
        validated_data['attendance_percentage'] = self._calculate_percentage(calc_data)
        validated_data['punctuality_score'] = self._calculate_punctuality_score(calc_data)
        
        # Handle percentage change - ensure both are Decimal
        prev_percentage = calc_data['previous_month_percentage']
        if isinstance(prev_percentage, float):
            prev_percentage = Decimal(str(prev_percentage))
            
        if prev_percentage > 0:
            validated_data['percentage_change'] = (
                validated_data['attendance_percentage'] - prev_percentage
            )
        else:
            validated_data['percentage_change'] = Decimal('0.00')
        
        # Handle finalization
        is_finalized = validated_data.get('is_finalized', instance.is_finalized)
        if is_finalized and not instance.is_finalized:
            validated_data['finalized_at'] = timezone.now()
        elif not is_finalized and instance.is_finalized:
            validated_data['finalized_at'] = None
        
        # Set updated_by from request context - THIS WILL NOW WORK
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)
# ======================= ATTENDANCE CONFIGURATION SERIALIZERS =======================

class AttendanceConfigurationListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for configuration listings"""
    section_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceConfiguration
        fields = [
            'id', 'section', 'section_name', 'school_start_time', 
            'school_end_time', 'min_attendance_percentage'
        ]
    
    def get_section_name(self, obj):
        if obj.section and not obj.section.deleted:
            return obj.section.name
        return None


class AttendanceConfigurationSerializer(serializers.ModelSerializer):
    """Attendance configuration serializer"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    section_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceConfiguration
        fields = [
            'id', 'section', 'section_detail',
            'school_start_time', 'school_end_time',
            'late_arrival_threshold', 'min_attendance_percentage',
            'half_day_threshold', 'auto_generate_reports', 'report_generation_day',
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
    
    def validate_section(self, value):
        """Validate section is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected section has been deleted.")
        
        # Check unique constraint (exclude soft deleted)
        qs = AttendanceConfiguration.objects.filter(section=value, deleted=False)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        
        if qs.exists():
            raise serializers.ValidationError("Configuration for this section already exists.")
        
        return value
    
    def validate_late_arrival_threshold(self, value):
        if value > 240:  # 4 hours
            raise serializers.ValidationError('Late arrival threshold cannot exceed 4 hours (240 minutes).')
        if value < 0:
            raise serializers.ValidationError('Late arrival threshold cannot be negative.')
        return value
    
    def validate_min_attendance_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Minimum attendance percentage must be between 0 and 100.')
        return value
    
    def validate_report_generation_day(self, value):
        if value < 1 or value > 28:
            raise serializers.ValidationError('Report generation day must be between 1 and 28.')
        return value
    
    def validate(self, attrs):
        """Validate time fields"""
        start_time = attrs.get('school_start_time', self.instance.school_start_time if self.instance else None)
        end_time = attrs.get('school_end_time', self.instance.school_end_time if self.instance else None)
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'school_end_time': 'School end time must be after start time.'
            })
        
        return attrs
    
    def to_representation(self, instance):
        # Handle soft deleted records
        if instance.deleted:
            return {
                'id': instance.id,
                'section': instance.section_id,
                'message': 'Attendance configuration has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ======================= ATTENDANCE SUMMARY SERIALIZERS =======================

class AttendanceSummaryListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for summary listings"""
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'student', 'student_name', 'current_year', 
            'overall_percentage', 'current_streak'
        ]
    
    def get_student_name(self, obj):
        if obj.student and not obj.student.deleted:
            return obj.student.user.get_full_name()
        return None


class AttendanceSummarySerializer(serializers.ModelSerializer):
    """Attendance summary serializer"""
    student_detail = serializers.SerializerMethodField()
    needs_improvement = serializers.SerializerMethodField()
    attendance_trend = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'student', 'student_detail', 'current_year',
            'total_days', 'days_present', 'days_absent', 'days_late',
            'days_half_day', 'days_excused', 'overall_percentage',
            'current_streak', 'last_calculated',
            'needs_improvement', 'attendance_trend'
        ]
        read_only_fields = ('last_calculated', 'overall_percentage')
    
    def get_student_detail(self, obj):
        if obj.student and not obj.student.deleted:
            from apps.users.serializers import StudentListingSerializer
            return StudentListingSerializer(obj.student).data
        return None
    
    def get_needs_improvement(self, obj):
        """Check if attendance needs improvement"""
        if obj.student and obj.student.deleted:
            return None
        try:
            config = AttendanceConfiguration.objects.get(
                section=obj.student.section, 
                deleted=False
            )
            return obj.overall_percentage < config.min_attendance_percentage
        except (AttendanceConfiguration.DoesNotExist, AttributeError):
            return obj.overall_percentage < 75.0
    
    def get_attendance_trend(self, obj):
        """Get attendance trend based on recent reports"""
        if obj.student and obj.student.deleted:
            return None
        try:
            recent_reports = MonthlyAttendanceReport.objects.filter(
                student=obj.student,
                deleted=False
            ).order_by('-year', '-month')[:3]
            
            if len(recent_reports) < 2:
                return "insufficient_data"
            
            percentages = [r.attendance_percentage for r in recent_reports]
            avg_change = sum(
                float(percentages[i]) - float(percentages[i+1]) 
                for i in range(len(percentages)-1)
            ) / (len(percentages) - 1)
            
            if avg_change > 2:
                return "improving"
            elif avg_change < -2:
                return "declining"
            return "stable"
        except Exception:
            return "stable"
    
    def validate_student(self, value):
        """Validate student is not deleted"""
        if value and value.deleted:
            raise serializers.ValidationError("Selected student has been deleted.")
        return value
    
    def _calculate_overall_percentage(self, data):
        """Calculate overall attendance percentage"""
        total = data.get('total_days', 0)
        excused = data.get('days_excused', 0)
        present = data.get('days_present', 0)
        half = data.get('days_half_day', 0)
        
        if total > 0:
            effective_days = total - excused
            if effective_days > 0:
                effective_present = present + (half * 0.5)
                return round((effective_present / effective_days) * 100, 2)
        return 0
    
    def create(self, validated_data):
        """Auto-calculate overall percentage"""
        validated_data['overall_percentage'] = self._calculate_overall_percentage(validated_data)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Recalculate overall percentage on update"""
        calc_data = {
            'total_days': validated_data.get('total_days', instance.total_days),
            'days_present': validated_data.get('days_present', instance.days_present),
            'days_half_day': validated_data.get('days_half_day', instance.days_half_day),
            'days_excused': validated_data.get('days_excused', instance.days_excused),
        }
        validated_data['overall_percentage'] = self._calculate_overall_percentage(calc_data)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        # Handle soft deleted student
        if instance.student and instance.student.deleted:
            return {
                'student': instance.student_id,
                'message': 'Associated student has been deleted'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('last_calculated'), str):
            data['last_calculated'] = data['last_calculated'].replace('T', ' ').split('.')[0]
        
        return data


# ======================= BULK ATTENDANCE SERIALIZERS =======================

class BulkAttendanceItemSerializer(serializers.Serializer):
    """Serializer for individual attendance entry in bulk operation"""
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=AttendanceStatus.choices)
    check_in_time = serializers.TimeField(required=False, allow_null=True)
    check_out_time = serializers.TimeField(required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, default='')


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for marking attendance in bulk"""
    section = serializers.IntegerField()
    date = serializers.DateField()
    subject = serializers.IntegerField(required=False, allow_null=True)
    marked_by = serializers.IntegerField()
    attendances = BulkAttendanceItemSerializer(many=True, min_length=1)
    
    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Attendance date cannot be in the future.")
        return value
    
    def validate_section(self, value):
        from apps.academic.models import Section
        try:
            section = Section.objects.get(id=value, deleted=False)
            return section
        except Section.DoesNotExist:
            raise serializers.ValidationError("Section not found or has been deleted.")
    
    def validate_subject(self, value):
        if value is None:
            return None
        from apps.academic.models import Subject
        try:
            subject = Subject.objects.get(id=value, deleted=False)
            return subject
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Subject not found or has been deleted.")
    
    def validate_marked_by(self, value):
        from apps.users.models import Teacher
        try:
            teacher = Teacher.objects.get(id=value, deleted=False)
            return teacher
        except Teacher.DoesNotExist:
            raise serializers.ValidationError("Teacher not found or has been deleted.")
    
    def validate_attendances(self, value):
        """Validate each attendance entry"""
        from apps.users.models import Student
        
        student_ids = [entry['student_id'] for entry in value]
        
        # Check for duplicate student IDs
        if len(student_ids) != len(set(student_ids)):
            raise serializers.ValidationError("Duplicate student IDs found in attendance list.")
        
        # Validate all students exist and are not deleted
        existing_students = Student.objects.filter(
            id__in=student_ids, 
            deleted=False
        ).values_list('id', flat=True)
        
        missing_students = set(student_ids) - set(existing_students)
        if missing_students:
            raise serializers.ValidationError(
                f"Students with IDs {list(missing_students)} not found or have been deleted."
            )
        
        # Validate check_in_time for late status
        for entry in value:
            if entry['status'] == AttendanceStatus.LATE and not entry.get('check_in_time'):
                raise serializers.ValidationError(
                    f"Check-in time is required for late attendance (Student ID: {entry['student_id']})."
                )
        
        return value
    
    def validate(self, attrs):
        """Check for existing attendance records"""
        section = attrs['section']
        date = attrs['date']
        subject = attrs.get('subject')
        attendances = attrs['attendances']
        
        student_ids = [entry['student_id'] for entry in attendances]
        
        # Check for existing records (exclude soft deleted)
        existing = DailyAttendance.objects.filter(
            student_id__in=student_ids,
            date=date,
            subject=subject,
            deleted=False
        ).values_list('student_id', flat=True)
        
        if existing:
            raise serializers.ValidationError(
                f"Attendance already exists for students with IDs {list(existing)} on {date}."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create bulk attendance records"""
        section = validated_data['section']
        date = validated_data['date']
        subject = validated_data.get('subject')
        marked_by = validated_data['marked_by']
        attendances = validated_data['attendances']
        
        created_records = []
        for entry in attendances:
            record = DailyAttendance.objects.create(
                student_id=entry['student_id'],
                date=date,
                status=entry['status'],
                subject=subject,
                section=section,
                marked_by=marked_by,
                check_in_time=entry.get('check_in_time'),
                check_out_time=entry.get('check_out_time'),
                remarks=entry.get('remarks', '')
            )
            created_records.append(record)
        
        return created_records


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics response"""
    total_students = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    half_day_count = serializers.IntegerField()
    excused_count = serializers.IntegerField()
    sick_leave_count = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    date = serializers.DateField()
    section_id = serializers.IntegerField()
    section_name = serializers.CharField()


class StudentAttendanceHistorySerializer(serializers.Serializer):
    """Serializer for student attendance history"""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    date_range_start = serializers.DateField()
    date_range_end = serializers.DateField()
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    half_days = serializers.IntegerField()
    excused_days = serializers.IntegerField()
    sick_leave_days = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    records = DailyAttendanceListingSerializer(many=True)