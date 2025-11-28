from django.urls import include, path
from .views import (
    FeeTypeView,
    FeeStructureView,
    FeeInvoiceView,
    FeeInvoiceItemView,
    FeePaymentView,
    FeeDiscountView,
    StudentDiscountView
)

urlpatterns = [
    path('v1/fee/type/', FeeTypeView.as_view()),
    path('v1/fee/structure/', FeeStructureView.as_view()),
    path('v1/fee/invoice/', FeeInvoiceView.as_view()),
    path('v1/fee/invoice/item/', FeeInvoiceItemView.as_view()),
    path('v1/fee/payment/', FeePaymentView.as_view()),
    path('v1/fee/discount/', FeeDiscountView.as_view()),
    path('v1/fee/student/discount/', StudentDiscountView.as_view()),
]