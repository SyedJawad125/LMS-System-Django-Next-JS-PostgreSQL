from django.db import models

from apps.users.models import Student, User
from utils.enums import *
from utils.reusable_classes import TimeUserStamps

# Create your models here.

class CertificateTemplate(TimeUserStamps):
    """Certificate Templates"""
    name = models.CharField(max_length=100)
    certificate_type = models.CharField(max_length=50)  # Completion, Merit, etc.
    template_file = models.FileField(upload_to='certificate_templates/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'certificate_templates'


class Certificate(TimeUserStamps):
    """Issued Certificates"""
    certificate_number = models.CharField(max_length=50, unique=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    issue_date = models.DateField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    certificate_file = models.FileField(upload_to='certificates/')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'certificates'


class Document(TimeUserStamps):
    """Student Documents"""
    DOCUMENT_TYPES = (
        (BIRTH_CERTIFICATE, BIRTH_CERTIFICATE),
        (TRANSFER_CERTIFICATE, TRANSFER_CERTIFICATE),
        (MARKSHEET, MARKSHEET),
        (ID_PROOF, ID_PROOF),
        (ADDRESS_PROOF, ADDRESS_PROOF),
        (MEDICAL, MEDICAL),
        (OTHER, OTHER),
)
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='student_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'documents'



# class CertificateTemplate(TimeUserStamps):
    """
    Certificate Templates - Stores reusable certificate templates that can be used to issue certificates.
    Admins can upload template files (PDF/DOCX/Images) with customizable names and types (Merit, Completion, etc.).
    Templates can be activated/deactivated and include descriptions for easy identification.
    """


# class Certificate(TimeUserStamps):
    """
    Issued Certificates - Manages certificates issued to students with auto-generated unique certificate numbers.
    Links students with certificate templates and stores the final issued certificate file.
    Tracks who issued the certificate and when, supporting various certificate types like Merit, Completion, Excellence.
    Certificate numbers are auto-generated in format CERT-YYYY-NNNN (e.g., CERT-2024-0001).
    """


# class Document(TimeUserStamps):
    """
    Student Documents - Manages all document uploads for students including official records and proofs.
    Supports multiple document types: birth certificates, transfer certificates, marksheets, ID proofs, address proofs, medical certificates, and others.
    Tracks who uploaded each document and when, with support for various file formats (PDF, Word, Excel, Images).
    Each student can have multiple documents of different types stored for admission and record-keeping purposes.
    """