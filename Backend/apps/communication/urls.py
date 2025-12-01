from django.urls import include, path
from .views import (
    AnnouncementView,
    EventView,
    MessageView,
    NotificationView
)

urlpatterns = [
    path('v1/announcements/', AnnouncementView.as_view()),
    path('v1/events/', EventView.as_view()),
    path('v1/messages/', MessageView.as_view()),
    path('v1/notifications/', NotificationView.as_view()),
]