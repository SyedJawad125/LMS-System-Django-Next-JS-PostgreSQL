from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import ( TimeSlotSerializer, TimetableSerializer)
from .filters import ( TimeSlotFilter, TimetableFilter)


class TimeSlotView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TimeSlotSerializer
    filterset_class = TimeSlotFilter

    @permission_required([CREATE_TIME_SLOT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_TIME_SLOT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_TIME_SLOT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_TIME_SLOT])
    def delete(self, request):
        return super().delete_(request)


class TimetableView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TimetableSerializer
    filterset_class = TimetableFilter

    @permission_required([CREATE_TIME_TABLE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_TIME_TABLE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_TIME_TABLE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_TIME_TABLE])
    def delete(self, request):
        return super().delete_(request)
