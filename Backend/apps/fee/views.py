from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    FeeTypeSerializer,
    FeeStructureSerializer,
    FeeInvoiceSerializer,
    FeeInvoiceItemSerializer,
    FeePaymentSerializer,
    FeeDiscountSerializer,
    StudentDiscountSerializer
)
from .filters import (
    FeeTypeFilter,
    FeeStructureFilter,
    FeeInvoiceFilter,
    FeeInvoiceItemFilter,
    FeePaymentFilter,
    FeeDiscountFilter,
    StudentDiscountFilter
)


class FeeTypeView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeeTypeSerializer
    filterset_class = FeeTypeFilter

    @permission_required([CREATE_FEE_TYPE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_FEE_TYPE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_FEE_TYPE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_FEE_TYPE])
    def delete(self, request):
        return super().delete_(request)


class FeeStructureView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeeStructureSerializer
    filterset_class = FeeStructureFilter

    @permission_required([CREATE_FEE_STRUCTURE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_FEE_STRUCTURE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_FEE_STRUCTURE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_FEE_STRUCTURE])
    def delete(self, request):
        return super().delete_(request)


class FeeInvoiceView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeeInvoiceSerializer
    filterset_class = FeeInvoiceFilter

    @permission_required([CREATE_FEE_INVOICE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_FEE_INVOICE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_FEE_INVOICE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_FEE_INVOICE])
    def delete(self, request):
        return super().delete_(request)


class FeeInvoiceItemView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeeInvoiceItemSerializer
    filterset_class = FeeInvoiceItemFilter

    @permission_required([CREATE_FEE_INVOICE_ITEM])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_FEE_INVOICE_ITEM])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_FEE_INVOICE_ITEM])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_FEE_INVOICE_ITEM])
    def delete(self, request):
        return super().delete_(request)


class FeePaymentView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeePaymentSerializer
    filterset_class = FeePaymentFilter

    @permission_required([CREATE_FEE_PAYMENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_FEE_PAYMENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_FEE_PAYMENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_FEE_PAYMENT])
    def delete(self, request):
        return super().delete_(request)


class FeeDiscountView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FeeDiscountSerializer
    filterset_class = FeeDiscountFilter

    @permission_required([CREATE_FEE_DISCOUNT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_FEE_DISCOUNT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_FEE_DISCOUNT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_FEE_DISCOUNT])
    def delete(self, request):
        return super().delete_(request)


class StudentDiscountView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentDiscountSerializer
    filterset_class = StudentDiscountFilter

    @permission_required([CREATE_STUDENT_DISCOUNT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_STUDENT_DISCOUNT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_STUDENT_DISCOUNT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_STUDENT_DISCOUNT])
    def delete(self, request):
        return super().delete_(request)