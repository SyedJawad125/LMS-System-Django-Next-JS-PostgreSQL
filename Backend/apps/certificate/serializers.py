from datetime import date
from rest_framework import serializers
from .models import CertificateTemplate, Certificate, Document
from apps.users.serializers import StudentListSerializer, UserListSerializer


# ==================== Certificate Template Serializers ====================

class CertificateTemplateListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for certificate template listings"""
    
    class Meta:
        model = CertificateTemplate
        fields = ['id', 'name', 'certificate_type', 'is_active']


class CertificateTemplateSerializer(serializers.ModelSerializer):
    """Full certificate template serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    certificates_count = serializers.SerializerMethodField()
    template_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CertificateTemplate
        fields = [
            'id', 'name', 'certificate_type', 'template_file', 'description',
            'is_active', 'template_file_url', 'certificates_count',
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
    
    def get_certificates_count(self, obj):
        """Count certificates issued using this template"""
        if obj.deleted:
            return 0
        return obj.certificate_set.filter(deleted=False).count()
    
    def get_template_file_url(self, obj):
        """Get the full URL for the template file"""
        if obj.template_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.template_file.url)
            return obj.template_file.url
        return None
    
    def validate_name(self, value):
        """Validate template name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Template name must be at least 2 characters long")
        return value.strip()
    
    def validate_certificate_type(self, value):
        """Validate certificate type"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Certificate type must be at least 2 characters long")
        return value.strip()
    
    def validate_template_file(self, value):
        """Validate template file"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Template file size cannot exceed 5MB")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.png', '.jpg', '.jpeg']
            file_ext = value.name.lower().split('.')[-1]
            if f'.{file_ext}' not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
                )
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'name': instance.name,
                'message': f'Certificate template "{instance.name}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Certificate Serializers ====================

class CertificateListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for certificate listings"""
    student_name = serializers.SerializerMethodField()
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'student_name', 'template_name',
            'title', 'issue_date'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None


class CertificateSerializer(serializers.ModelSerializer):
    """Full certificate serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    template_detail = serializers.SerializerMethodField()
    issued_by_detail = serializers.SerializerMethodField()
    certificate_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'student', 'template', 'issue_date',
            'title', 'description', 'certificate_file', 'issued_by',
            'student_detail', 'template_detail', 'issued_by_detail',
            'certificate_file_url',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'certificate_number', 'created_at', 'updated_at', 
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
    
    def get_template_detail(self, obj):
        if obj.template and not obj.template.deleted:
            return CertificateTemplateListingSerializer(obj.template).data
        return None
    
    def get_issued_by_detail(self, obj):
        if obj.issued_by and not obj.issued_by.deleted:
            return UserListSerializer(obj.issued_by).data
        return None
    
    def get_certificate_file_url(self, obj):
        """Get the full URL for the certificate file"""
        if obj.certificate_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.certificate_file.url)
            return obj.certificate_file.url
        return None
    
    def validate_student(self, value):
        """Validate student"""
        if value.deleted:
            raise serializers.ValidationError("Cannot issue certificate to a deleted student")
        return value
    
    def validate_template(self, value):
        """Validate template"""
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted certificate template")
        if value and not value.is_active:
            raise serializers.ValidationError("Cannot use an inactive certificate template")
        return value
    
    def validate_title(self, value):
        """Validate certificate title"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Certificate title must be at least 3 characters long")
        return value.strip()
    
    def validate_description(self, value):
        """Validate certificate description"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Certificate description must be at least 10 characters long")
        return value.strip()
    
    def validate_issue_date(self, value):
        """Validate issue date"""
        if value > date.today():
            raise serializers.ValidationError("Issue date cannot be in the future")
        return value
    
    def validate_certificate_file(self, value):
        """Validate certificate file"""
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Certificate file size cannot exceed 10MB")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
            file_ext = value.name.lower().split('.')[-1]
            if f'.{file_ext}' not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
                )
        return value
    
    def create(self, validated_data):
        """Auto-generate certificate number on creation"""
        # Generate certificate number if not provided
        if not validated_data.get('certificate_number'):
            # Get last certificate number
            last_certificate = Certificate.objects.filter(
                deleted=False
            ).order_by('-id').first()
            
            if last_certificate and last_certificate.certificate_number:
                try:
                    # Extract number from last certificate (e.g., CERT-2024-0001)
                    last_number = int(last_certificate.certificate_number.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            # Generate certificate number: CERT-YYYY-NNNN
            year = date.today().year
            validated_data['certificate_number'] = f'CERT-{year}-{new_number:04d}'
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'certificate_number': instance.certificate_number,
                'message': f'Certificate "{instance.certificate_number}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Document Serializers ====================

class DocumentListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for document listings"""
    student_name = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'student_name', 'document_type', 'title',
            'uploaded_by_name', 'uploaded_at'
        ]
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            full_name = obj.student.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.student.user.username
        return None
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            full_name = obj.uploaded_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.uploaded_by.username
        return None


class DocumentSerializer(serializers.ModelSerializer):
    """Full document serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    student_detail = serializers.SerializerMethodField()
    uploaded_by_detail = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'student', 'document_type', 'title', 'file',
            'uploaded_by', 'uploaded_at',
            'student_detail', 'uploaded_by_detail', 'file_url', 'file_size',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'uploaded_at', 'created_at', 'updated_at', 
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
    
    def get_uploaded_by_detail(self, obj):
        if obj.uploaded_by and not obj.uploaded_by.deleted:
            return UserListSerializer(obj.uploaded_by).data
        return None
    
    def get_file_url(self, obj):
        """Get the full URL for the document file"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size(self, obj):
        """Get file size in human-readable format"""
        if obj.file:
            size_bytes = obj.file.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
        return None
    
    def validate_student(self, value):
        """Validate student"""
        if value.deleted:
            raise serializers.ValidationError("Cannot upload document for a deleted student")
        return value
    
    def validate_title(self, value):
        """Validate document title"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Document title must be at least 3 characters long")
        return value.strip()
    
    def validate_file(self, value):
        """Validate document file"""
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Document file size cannot exceed 10MB")
            
            # Check file extension
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', 
                '.gif', '.txt', '.xls', '.xlsx'
            ]
            file_ext = value.name.lower().split('.')[-1]
            if f'.{file_ext}' not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
                )
        return value
    
    def validate_document_type(self, value):
        """Validate document type against allowed choices"""
        valid_types = [choice[0] for choice in Document.DOCUMENT_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid document type. Must be one of: {', '.join(valid_types)}"
            )
        return value
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Document "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('uploaded_at'), str):
            data['uploaded_at'] = data['uploaded_at'].replace('T', ' ').split('.')[0]
        
        return data