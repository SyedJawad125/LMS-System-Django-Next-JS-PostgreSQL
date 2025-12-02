from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    ReportCardSerializer,
    StudentBehaviorSerializer
)
from .filters import (
    ReportCardFilter,
    StudentBehaviorFilter
)


class ReportCardView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportCardSerializer
    filterset_class = ReportCardFilter

    @permission_required([CREATE_REPORT_CARD])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_REPORT_CARD])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_REPORT_CARD])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_REPORT_CARD])
    def delete(self, request):
        return super().delete_(request)


class StudentBehaviorView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentBehaviorSerializer
    filterset_class = StudentBehaviorFilter

    @permission_required([CREATE_STUDENT_BEHAVIOR])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_STUDENT_BEHAVIOR])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_STUDENT_BEHAVIOR])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_STUDENT_BEHAVIOR])
    def delete(self, request):
        return super().delete_(request)