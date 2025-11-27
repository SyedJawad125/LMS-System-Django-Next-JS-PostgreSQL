from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    ExamTypeSerializer, 
    ExamSerializer, 
    ExamScheduleSerializer, 
    ExamResultSerializer, 
    GradeSystemSerializer
)
from .filters import (
    ExamTypeFilter, 
    ExamFilter, 
    ExamScheduleFilter, 
    ExamResultFilter, 
    GradeSystemFilter
)


class ExamTypeView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExamTypeSerializer
    filterset_class = ExamTypeFilter

    @permission_required([CREATE_EXAM_TYPE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_EXAM_TYPE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_EXAM_TYPE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_EXAM_TYPE])
    def delete(self, request):
        return super().delete_(request)


class ExamView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExamSerializer
    filterset_class = ExamFilter

    @permission_required([CREATE_EXAM])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_EXAM])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_EXAM])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_EXAM])
    def delete(self, request):
        return super().delete_(request)


class ExamScheduleView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExamScheduleSerializer
    filterset_class = ExamScheduleFilter

    @permission_required([CREATE_EXAM_SCHEDULE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_EXAM_SCHEDULE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_EXAM_SCHEDULE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_EXAM_SCHEDULE])
    def delete(self, request):
        return super().delete_(request)


class ExamResultView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExamResultSerializer
    filterset_class = ExamResultFilter

    @permission_required([CREATE_EXAM_RESULT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_EXAM_RESULT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_EXAM_RESULT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_EXAM_RESULT])
    def delete(self, request):
        return super().delete_(request)


class GradeSystemView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GradeSystemSerializer
    filterset_class = GradeSystemFilter

    @permission_required([CREATE_GRADE_SYSTEM])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_GRADE_SYSTEM])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_GRADE_SYSTEM])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_GRADE_SYSTEM])
    def delete(self, request):
        return super().delete_(request)