from django.urls import include, path
from .views import (
    AnnouncementView,
    EventView,
    MessageView,
    NotificationView
)

urlpatterns = [
    path('v1/announcement/', AnnouncementView.as_view()),
    path('v1/event/', EventView.as_view()),
    path('v1/messages/', MessageView.as_view()),
    path('v1/notifications/', NotificationView.as_view()),
]