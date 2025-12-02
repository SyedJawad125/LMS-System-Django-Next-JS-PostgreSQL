from rest_framework import serializers
from .models import SchoolSettings, EmailTemplate, SMSTemplate, AuditLog
from apps.users.serializers import UserListSerializer


# ==================== School Settings Serializers ====================

class SchoolSettingsListSerializer(serializers.ModelSerializer):
    """Minimal serializer for school settings listings"""
    
    class Meta:
        model = SchoolSettings
        fields = ['id', 'school_name', 'school_code', 'email', 'phone']


class SchoolSettingsSerializer(serializers.ModelSerializer):
    """Full school settings serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolSettings
        fields = [
            'id', 'school_name', 'school_code', 'logo', 'logo_url', 'email', 
            'phone', 'website', 'address', 'established_year', 'principal_name',
            'academic_year_start_month', 'currency', 'timezone',
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
    
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
    
    def validate_school_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("School name must be at least 2 characters long")
        return value.strip()
    
    def validate_school_code(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("School code must be at least 2 characters long")
        return value.strip().upper()
    
    def validate_email(self, value):
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid email address")
        return value.strip().lower()
    
    def validate_phone(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 characters long")
        return value.strip()
    
    def validate_established_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1800 or value > current_year:
            raise serializers.ValidationError(f"Established year must be between 1800 and {current_year}")
        return value
    
    def validate_academic_year_start_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Academic year start month must be between 1 and 12")
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'school_name': instance.school_name,
                'message': f'School settings "{instance.school_name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Email Template Serializers ====================

class EmailTemplateListSerializer(serializers.ModelSerializer):
    """Minimal serializer for email template listings"""
    
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'template_type', 'is_active']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Full email template serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'subject', 'body', 'template_type', 'is_active',
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
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Template name must be at least 2 characters long")
        return value.strip()
    
    def validate_subject(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Email subject must be at least 2 characters long")
        return value.strip()
    
    def validate_body(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Email body must be at least 10 characters long")
        return value.strip()
    
    def validate_template_type(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Template type must be at least 2 characters long")
        return value.strip().lower()
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Email template "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== SMS Template Serializers ====================

class SMSTemplateListSerializer(serializers.ModelSerializer):
    """Minimal serializer for SMS template listings"""
    message_length = serializers.SerializerMethodField()
    
    class Meta:
        model = SMSTemplate
        fields = ['id', 'name', 'template_type', 'is_active', 'message_length']
    
    def get_message_length(self, obj):
        return len(obj.message)


class SMSTemplateSerializer(serializers.ModelSerializer):
    """Full SMS template serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    message_length = serializers.SerializerMethodField()
    characters_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = SMSTemplate
        fields = [
            'id', 'name', 'message', 'template_type', 'is_active',
            'message_length', 'characters_remaining',
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
    
    def get_message_length(self, obj):
        return len(obj.message)
    
    def get_characters_remaining(self, obj):
        return 160 - len(obj.message)
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Template name must be at least 2 characters long")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("SMS message must be at least 5 characters long")
        if len(value) > 160:
            raise serializers.ValidationError(f"SMS message cannot exceed 160 characters. Current length: {len(value)}")
        return value.strip()
    
    def validate_template_type(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Template type must be at least 2 characters long")
        return value.strip().lower()
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'SMS template "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Audit Log Serializers ====================

class AuditLogListSerializer(serializers.ModelSerializer):
    """Minimal serializer for audit log listings"""
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'action', 'model_name', 'timestamp']
    
    def get_user_name(self, obj):
        if obj.user:
            full_name = obj.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.user.username
        return 'System'


class AuditLogSerializer(serializers.ModelSerializer):
    """Full audit log serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    change_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'model_name', 'object_id', 'changes',
            'ip_address', 'timestamp', 'user_detail', 'change_summary',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('timestamp', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
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
    
    def get_user_detail(self, obj):
        if obj.user and not obj.user.deleted:
            return UserListSerializer(obj.user).data
        return None
    
    def get_change_summary(self, obj):
        """Generate a human-readable summary of changes"""
        if not obj.changes:
            return "No changes recorded"
        
        try:
            changes_count = len(obj.changes.keys()) if isinstance(obj.changes, dict) else 0
            return f"{changes_count} field(s) modified"
        except:
            return "Changes recorded"
    
    def validate_action(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Action must be at least 2 characters long")
        
        # Common action types
        valid_actions = ['create', 'update', 'delete', 'view', 'login', 'logout', 'export', 'import']
        if value.lower() not in valid_actions:
            # Allow custom actions but warn
            pass
        
        return value.strip().lower()
    
    def validate_model_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Model name must be at least 2 characters long")
        return value.strip()
    
    def validate_object_id(self, value):
        if not value or len(str(value).strip()) < 1:
            raise serializers.ValidationError("Object ID is required")
        return str(value).strip()
    
    def validate_changes(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Changes must be a valid JSON object")
        return value
    
    def validate_ip_address(self, value):
        if value:
            # Basic IP validation
            import re
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'
            
            if not (re.match(ipv4_pattern, value) or re.match(ipv6_pattern, value)):
                raise serializers.ValidationError("Invalid IP address format")
        
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'action': instance.action,
                'model_name': instance.model_name,
                'message': f'Audit log for "{instance.action}" on "{instance.model_name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format timestamp
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = data['timestamp'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data