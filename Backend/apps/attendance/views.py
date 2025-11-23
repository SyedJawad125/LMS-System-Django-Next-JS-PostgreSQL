from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from apps.attendance.models import AttendanceSummary
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

    @permission_required([CREATE_DAILY_ATTENDANCE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_DAILY_ATTENDANCE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_DAILY_ATTENDANCE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_DAILY_ATTENDANCE])
    def delete(self, request):
        return super().delete_(request)


class MonthlyAttendanceReportView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MonthlyAttendanceReportSerializer
    filterset_class = MonthlyAttendanceReportFilter

    @permission_required([CREATE_MONTHLY_ATTENDANCE_REPORT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_MONTHLY_ATTENDANCE_REPORT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_MONTHLY_ATTENDANCE_REPORT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_MONTHLY_ATTENDANCE_REPORT])
    def delete(self, request):
        return super().delete_(request)


class AttendanceConfigurationView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttendanceConfigurationSerializer
    filterset_class = AttendanceConfigurationFilter

    @permission_required([CREATE_ATTENDANCE_CONFIGURATION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ATTENDANCE_CONFIGURATION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ATTENDANCE_CONFIGURATION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ATTENDANCE_CONFIGURATION])
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
    def get(self, request, student_id=None):
        """Handle both list and retrieve operations"""
        if student_id:
            # Single object retrieval by student_id (which is the PK)
            try:
                # Use pk instead of student_id since student is the primary key
                instance = AttendanceSummary.objects.get(pk=student_id)
                serializer = self.serializer_class(instance)
                # Use Response directly if BaseView methods aren't available
                from rest_framework.response import Response
                return Response({
                    'status': 'success',
                    'data': serializer.data,
                    'count': 1
                }, status=200)
            except AttendanceSummary.DoesNotExist:
                from rest_framework.response import Response
                return Response({
                    'status': 'error',
                    'message': 'Attendance summary not found'
                }, status=404)
        else:
            # List all objects
            return super().get_(request)

    @permission_required([UPDATE_ATTENDANCE_SUMMARY])
    def patch(self, request, student_id=None):
        """Update attendance summary using student_id from URL"""
        from rest_framework.response import Response
        
        if not student_id:
            return Response({
                'status': 'error',
                'message': 'Student ID is required in URL for update'
            }, status=400)
        
        try:
            # Use pk instead of student_id since student is the primary key
            instance = AttendanceSummary.objects.get(pk=student_id)
            
            # Update the record
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'status': 'success',
                'data': serializer.data,
                'count': 1
            }, status=200)
            
        except AttendanceSummary.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Attendance summary not found for this student'
            }, status=404)

    @permission_required([DELETE_ATTENDANCE_SUMMARY])
    def delete(self, request, student_id=None):
        """Delete attendance summary using student_id from URL"""
        from rest_framework.response import Response
        
        if not student_id:
            return Response({
                'status': 'error',
                'message': 'Student ID is required in URL for deletion'
            }, status=400)
        
        try:
            # Use pk instead of student_id since student is the primary key
            instance = AttendanceSummary.objects.get(pk=student_id)
            instance.delete()
            
            return Response({
                'status': 'success',
                'message': 'Attendance summary deleted successfully'
            }, status=200)
            
        except AttendanceSummary.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Attendance summary not found for this student'
            }, status=404)