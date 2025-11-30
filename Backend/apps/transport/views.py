from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (RouteSerializer, VehicleSerializer, TransportAllocationSerializer)
from .filters import (RouteFilter, VehicleFilter, TransportAllocationFilter)


class RouteView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RouteSerializer
    filterset_class = RouteFilter

    @permission_required([CREATE_ROUTE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ROUTE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ROUTE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ROUTE])
    def delete(self, request):
        return super().delete_(request)


class VehicleView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = VehicleSerializer
    filterset_class = VehicleFilter

    @permission_required([CREATE_VEHICLE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_VEHICLE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_VEHICLE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_VEHICLE])
    def delete(self, request):
        return super().delete_(request)


class TransportAllocationView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransportAllocationSerializer
    filterset_class = TransportAllocationFilter

    @permission_required([CREATE_TRANSPORT_ALLOCATION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_TRANSPORT_ALLOCATION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_TRANSPORT_ALLOCATION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_TRANSPORT_ALLOCATION])
    def delete(self, request):
        return super().delete_(request)