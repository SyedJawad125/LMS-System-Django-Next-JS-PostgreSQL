from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.users.urls')),
    # path('api/myapp/', include('apps.myapp.urls')),
    path('api/images/', include('apps.images.urls')),
    path('api/academic/', include('apps.academic.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/timetable/', include('apps.timetable.urls')),
    path('api/exams/', include('apps.exams.urls')),
    path('api/fee/', include('apps.fee.urls')),
    path('api/transport/', include('apps.transport.urls')),
    path('api/communication/', include('apps.communication.urls')),
    path('api/homework/assignment/', include('apps.homework_assignments.urls')),
    path('api/certificate/', include('apps.certificate.urls')),
    path('api/leave/', include('apps.leave.urls')),
    path('api/configuration/', include('apps.configuration.urls')),
    path('api/report/', include('apps.report.urls')),
    path('api/online/learning/', include('apps.online_learning.urls')),
    path('api/rag/', include('apps.rag_system.urls')),
    
    

    # path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
