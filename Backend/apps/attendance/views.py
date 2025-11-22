from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    DailyAttendanceSerializer, MonthlyAttendanceReportSerializer,
    AttendanceConfigurationSerializer, AttendanceSummarySerializer
)
from .filters import (
    DailyAttendanceFilter, MonthlyAttendanceReportFilter,
    AttendanceConfigurationFilter, AttendanceSummaryFilter
)

class DailyAttendanceView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DailyAttendanceSerializer
    filterset_class = DailyAttendanceFilter

    @permission_required([CREATE_ATTENDANCE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ATTENDANCE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ATTENDANCE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ATTENDANCE])
    def delete(self, request):
        return super().delete_(request)


class MonthlyAttendanceReportView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MonthlyAttendanceReportSerializer
    filterset_class = MonthlyAttendanceReportFilter

    @permission_required([CREATE_ATTENDANCE_REPORT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ATTENDANCE_REPORT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ATTENDANCE_REPORT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ATTENDANCE_REPORT])
    def delete(self, request):
        return super().delete_(request)


class AttendanceConfigurationView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttendanceConfigurationSerializer
    filterset_class = AttendanceConfigurationFilter

    @permission_required([CREATE_ATTENDANCE_CONFIG])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ATTENDANCE_CONFIG])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ATTENDANCE_CONFIG])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ATTENDANCE_CONFIG])
    def delete(self, request):
        return super().delete_(request)


class AttendanceSummaryView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttendanceSummarySerializer
    filterset_class = AttendanceSummaryFilter

    @permission_required([CREATE_ATTENDANCE_SUMMARY])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ATTENDANCE_SUMMARY])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ATTENDANCE_SUMMARY])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ATTENDANCE_SUMMARY])
    def delete(self, request):
        return super().delete_(request)