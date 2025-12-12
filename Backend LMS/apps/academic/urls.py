from django.urls import include, path
from .views import (
    AcademicYearView, DepartmentView, ClassView, 
    SectionView, SubjectView, ClassSubjectView
)

urlpatterns = [
    path('v1/academic/year/', AcademicYearView.as_view()),
    path('v1/department/', DepartmentView.as_view()),
    path('v1/class/', ClassView.as_view()),
    path('v1/section/', SectionView.as_view()),
    path('v1/subject/', SubjectView.as_view()),
    path('v1/class/subject/', ClassSubjectView.as_view()),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]