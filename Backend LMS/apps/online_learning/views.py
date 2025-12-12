from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from utils.base_api import BaseView
from utils.decorator import permission_required
from utils.permission_enums import *
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    CourseEnrollmentSerializer,
    LessonProgressSerializer,
    QuizSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
    QuizAttemptSerializer,
    QuizAnswerSerializer
)
from .filters import (
    CourseFilter,
    LessonFilter,
    CourseEnrollmentFilter,
    LessonProgressFilter,
    QuizFilter,
    QuestionFilter,
    QuestionOptionFilter,
    QuizAttemptFilter,
    QuizAnswerFilter
)


# Course Views
class CourseView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CourseSerializer
    filterset_class = CourseFilter

    @permission_required([CREATE_COURSE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_COURSE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_COURSE])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_COURSE])
    def delete(self, request):
        return super().delete_(request)


# Lesson Views
class LessonView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LessonSerializer
    filterset_class = LessonFilter

    @permission_required([CREATE_LESSON])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LESSON])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LESSON])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LESSON])
    def delete(self, request):
        return super().delete_(request)


# CourseEnrollment Views
class CourseEnrollmentView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CourseEnrollmentSerializer
    filterset_class = CourseEnrollmentFilter

    @permission_required([CREATE_COURSE_ENROLLMENT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_COURSE_ENROLLMENT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_COURSE_ENROLLMENT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_COURSE_ENROLLMENT])
    def delete(self, request):
        return super().delete_(request)


# LessonProgress Views
class LessonProgressView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LessonProgressSerializer
    filterset_class = LessonProgressFilter

    @permission_required([CREATE_LESSON_PROGRESS])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_LESSON_PROGRESS])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_LESSON_PROGRESS])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_LESSON_PROGRESS])
    def delete(self, request):
        return super().delete_(request)


# Quiz Views
class QuizView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizSerializer
    filterset_class = QuizFilter

    @permission_required([CREATE_QUIZ])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_QUIZ])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_QUIZ])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_QUIZ])
    def delete(self, request):
        return super().delete_(request)


# Question Views
class QuestionView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter

    @permission_required([CREATE_QUESTION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_QUESTION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_QUESTION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_QUESTION])
    def delete(self, request):
        return super().delete_(request)


# QuestionOption Views
class QuestionOptionView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionOptionSerializer
    filterset_class = QuestionOptionFilter

    @permission_required([CREATE_QUESTION_OPTION])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_QUESTION_OPTION])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_QUESTION_OPTION])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_QUESTION_OPTION])
    def delete(self, request):
        return super().delete_(request)


# QuizAttempt Views
class QuizAttemptView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizAttemptSerializer
    filterset_class = QuizAttemptFilter

    @permission_required([CREATE_QUIZ_ATTEMPT])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_QUIZ_ATTEMPT])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_QUIZ_ATTEMPT])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_QUIZ_ATTEMPT])
    def delete(self, request):
        return super().delete_(request)


# QuizAnswer Views
class QuizAnswerView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizAnswerSerializer
    filterset_class = QuizAnswerFilter

    @permission_required([CREATE_QUIZ_ANSWER])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_QUIZ_ANSWER])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_QUIZ_ANSWER])
    def patch(self, request):
        return super().patch_(request)
    
    @permission_required([DELETE_QUIZ_ANSWER])
    def delete(self, request):
        return super().delete_(request)