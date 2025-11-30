from django.urls import include, path
from .views import (RouteView, VehicleView, TransportAllocationView)

urlpatterns = [
    path('v1/route/', RouteView.as_view()),
    path('v1/vehicle/', VehicleView.as_view()),
    path('v1/transport/allocation/', TransportAllocationView.as_view()),
]