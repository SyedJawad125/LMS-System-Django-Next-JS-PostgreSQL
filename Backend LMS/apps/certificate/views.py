from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (CertificateTemplateSerializer, CertificateSerializer, DocumentSerializer)
from .filters import (CertificateTemplateFilter, CertificateFilter, DocumentFilter)


class CertificateTemplateView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CertificateTemplateSerializer
    filterset_class = CertificateTemplateFilter

    @permission_required([CREATE_CERTIFICATE_TEMPLATE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_CERTIFICATE_TEMPLATE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_CERTIFICATE_TEMPLATE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_CERTIFICATE_TEMPLATE])
    def delete(self, request):
        return super().delete_(request)


class CertificateView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CertificateSerializer
    filterset_class = CertificateFilter

    @permission_required([CREATE_CERTIFICATE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_CERTIFICATE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_CERTIFICATE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_CERTIFICATE])
    def delete(self, request):
        return super().delete_(request)


class DocumentView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DocumentSerializer
    filterset_class = DocumentFilter

    @permission_required([CREATE_DOCUMENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_DOCUMENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_DOCUMENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_DOCUMENT])
    def delete(self, request):
        return super().delete_(request)