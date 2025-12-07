from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RAGChatViewSet, DocumentManagementViewSet,
    index_database_tables, rag_metrics, clear_cache
)

router = DefaultRouter()
router.register(r'chat', RAGChatViewSet, basename='rag-chat')
router.register(r'documents', DocumentManagementViewSet, basename='rag-documents')

app_name = 'rag_system'

urlpatterns = [
    path('', include(router.urls)),
    path('v1/index/database/', index_database_tables, name='index-database'),
    path('v1/metrics/', rag_metrics, name='metrics'),
    path('v1/clear/cache/', clear_cache, name='clear-cache'),
]


"""
COMPLETE URL STRUCTURE:
=======================

BASE: /api/rag/

CHAT ENDPOINTS (ViewSet):
1. POST   /api/rag/chat/query/              # Main chat query
2. GET    /api/rag/chat/history/            # Get chat history  
3. DELETE /api/rag/chat/clear_history/      # Clear history

DOCUMENT ENDPOINTS (ModelViewSet):
4. GET    /api/rag/documents/               # List all documents
5. POST   /api/rag/documents/               # Upload document
6. GET    /api/rag/documents/{id}/          # Get single document
7. PUT    /api/rag/documents/{id}/          # Update document
8. PATCH  /api/rag/documents/{id}/          # Partial update
9. DELETE /api/rag/documents/{id}/          # Delete document

UTILITY ENDPOINTS (API Views):
10. POST   /api/rag/v1/index/database/      # Index database tables
11. GET    /api/rag/v1/metrics/             # Get system metrics
12. DELETE /api/rag/v1/clear/cache/         # Clear cache

TOTAL: 12 Endpoints
"""