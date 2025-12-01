from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer
)
from .filters import (
    AssignmentFilter,
    AssignmentSubmissionFilter
)


# Assignment View
class AssignmentView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AssignmentSerializer
    filterset_class = AssignmentFilter

    @permission_required([CREATE_ASSIGNMENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ASSIGNMENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ASSIGNMENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_ASSIGNMENT])
    def delete(self, request):
        return super().delete_(request)


# Assignment Submission View
class AssignmentSubmissionView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AssignmentSubmissionSerializer
    filterset_class = AssignmentSubmissionFilter

    @permission_required([CREATE_SUBMISSION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_SUBMISSION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_SUBMISSION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_SUBMISSION])
    def delete(self, request):
        return super().delete_(request)