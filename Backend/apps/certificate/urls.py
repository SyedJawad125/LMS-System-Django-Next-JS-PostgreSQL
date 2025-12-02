from django.urls import path
from .views import CertificateTemplateView, CertificateView, DocumentView

urlpatterns = [
    path('v1/certificate/template/', CertificateTemplateView.as_view()),
    path('v1/certificate/', CertificateView.as_view()),
    path('v1/document/', DocumentView.as_view()),
]