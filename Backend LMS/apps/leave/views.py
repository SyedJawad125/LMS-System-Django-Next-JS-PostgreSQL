from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    LeaveTypeSerializer,
    LeaveApplicationSerializer,
    LeaveBalanceSerializer,
    LeaveConfigurationSerializer,
    LeaveApprovalWorkflowSerializer,
    LeaveHistorySerializer
)
from .filters import (
    LeaveTypeFilter,
    LeaveApplicationFilter,
    LeaveBalanceFilter,
    LeaveConfigurationFilter,
    LeaveApprovalWorkflowFilter,
    LeaveHistoryFilter
)


class LeaveTypeView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaveTypeSerializer
    filterset_class = LeaveTypeFilter

    @permission_required([CREATE_LEAVE_TYPE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LEAVE_TYPE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LEAVE_TYPE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LEAVE_TYPE])
    def delete(self, request):
        return super().delete_(request)


class LeaveApplicationView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaveApplicationSerializer
    filterset_class = LeaveApplicationFilter

    @permission_required([CREATE_LEAVE_APPLICATION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LEAVE_APPLICATION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LEAVE_APPLICATION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LEAVE_APPLICATION])
    def delete(self, request):
        return super().delete_(request)


class LeaveBalanceView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaveBalanceSerializer
    filterset_class = LeaveBalanceFilter

    @permission_required([CREATE_LEAVE_BALANCE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LEAVE_BALANCE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LEAVE_BALANCE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LEAVE_BALANCE])
    def delete(self, request):
        return super().delete_(request)


class LeaveConfigurationView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaveConfigurationSerializer
    filterset_class = LeaveConfigurationFilter

    @permission_required([CREATE_LEAVE_CONFIGURATION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LEAVE_CONFIGURATION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LEAVE_CONFIGURATION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LEAVE_CONFIGURATION])
    def delete(self, request):
        return super().delete_(request)


class LeaveApprovalWorkflowView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaveApprovalWorkflowSerializer
    filterset_class = LeaveApprovalWorkflowFilter

    @permission_required([CREATE_LEAVE_APPROVAL_WORKFLOW])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LEAVE_APPROVAL_WORKFLOW])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LEAVE_APPROVAL_WORKFLOW])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LEAVE_APPROVAL_WORKFLOW])
    def delete(self, request):
        return super().delete_(request)


class LeaveHistoryView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaveHistorySerializer  
    filterset_class = LeaveHistoryFilter

    @permission_required([READ_LEAVE_HISTORY])  # History is typically read-only
    def get(self, request):
        return super().get_(request)