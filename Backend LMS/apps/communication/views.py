from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    AnnouncementSerializer,
    EventSerializer,
    MessageSerializer,
    NotificationSerializer
)
from .filters import (
    AnnouncementFilter,
    EventFilter,
    MessageFilter,
    NotificationFilter
)


class AnnouncementView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AnnouncementSerializer
    filterset_class = AnnouncementFilter

    @permission_required([CREATE_ANNOUNCEMENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ANNOUNCEMENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ANNOUNCEMENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ANNOUNCEMENT])
    def delete(self, request):
        return super().delete_(request)


class EventView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer
    filterset_class = EventFilter

    @permission_required([CREATE_EVENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_EVENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_EVENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_EVENT])
    def delete(self, request):
        return super().delete_(request)


class MessageView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    filterset_class = MessageFilter

    @permission_required([CREATE_MESSAGE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_MESSAGE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_MESSAGE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_MESSAGE])
    def delete(self, request):
        return super().delete_(request)


class NotificationView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    filterset_class = NotificationFilter

    @permission_required([CREATE_NOTIFICATION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_NOTIFICATION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_NOTIFICATION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_NOTIFICATION])
    def delete(self, request):
        return super().delete_(request)