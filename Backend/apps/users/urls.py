from django.urls import path
from .views import (LoginView, RefreshView, LogoutView, ForgetPasswordView, VerifyLinkView, ResetPasswordView,
                    PermissionView, EmployeeView, EmployeeToggleView, RoleView, AccountActivateView)

urlpatterns = [
    path('v1/login/', LoginView.as_view()),
    path('v1/refresh/', RefreshView.as_view()),
    path('v1/logout/', LogoutView.as_view()),

    path('v1/forget/password/', ForgetPasswordView.as_view()),
    path('v1/verify/link/', VerifyLinkView.as_view()),
    path('v1/reset/password/', ResetPasswordView.as_view()),

    path('v1/employee/', EmployeeView.as_view()),
    path('v1/toggle/', EmployeeToggleView.as_view()),

    path('v1/permission/', PermissionView.as_view()),
    path('v1/role/', RoleView.as_view()),

    path('v1/account/activate/', AccountActivateView.as_view()),

]
