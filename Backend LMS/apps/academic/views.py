from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    AcademicYearSerializer, DepartmentSerializer, ClassSerializer, 
    SectionSerializer, SubjectSerializer, ClassSubjectSerializer
)
from .filters import (
    AcademicYearFilter, DepartmentFilter, ClassFilter, 
    SectionFilter, SubjectFilter, ClassSubjectFilter
)


class AcademicYearView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AcademicYearSerializer
    filterset_class = AcademicYearFilter

    @permission_required([CREATE_ACADEMIC_YEAR])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ACADEMIC_YEAR])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ACADEMIC_YEAR])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ACADEMIC_YEAR])
    def delete(self, request):
        return super().delete_(request)


class DepartmentView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentSerializer
    filterset_class = DepartmentFilter

    @permission_required([CREATE_DEPARTMENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_DEPARTMENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_DEPARTMENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_DEPARTMENT])
    def delete(self, request):
        return super().delete_(request)


class ClassView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClassSerializer
    filterset_class = ClassFilter

    @permission_required([CREATE_CLASS])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_CLASS])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_CLASS])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_CLASS])
    def delete(self, request):
        return super().delete_(request)


class SectionView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SectionSerializer
    filterset_class = SectionFilter

    @permission_required([CREATE_SECTION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_SECTION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_SECTION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_SECTION])
    def delete(self, request):
        return super().delete_(request)


class SubjectView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubjectSerializer
    filterset_class = SubjectFilter

    @permission_required([CREATE_SUBJECT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_SUBJECT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_SUBJECT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_SUBJECT])
    def delete(self, request):
        return super().delete_(request)


class ClassSubjectView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClassSubjectSerializer
    filterset_class = ClassSubjectFilter

    @permission_required([CREATE_CLASS_SUBJECT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_CLASS_SUBJECT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_CLASS_SUBJECT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_CLASS_SUBJECT])
    def delete(self, request):
        return super().delete_(request)