# ============================================
# UPDATED URLS FOR VECTOR-STORE RAG
# File: apps/rag_system/urls.py
# ============================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VectorStoreRAGChatViewSet, DocumentManagementViewSet,
    initialize_vectorstore, rag_metrics, clear_cache, system_status
)

router = DefaultRouter()
router.register(r'chat', VectorStoreRAGChatViewSet, basename='rag-chat')
router.register(r'documents', DocumentManagementViewSet, basename='rag-documents')

app_name = 'rag_system'

urlpatterns = [
    path('', include(router.urls)),
    path('v1/initialize/', initialize_vectorstore, name='initialize-vectorstore'),
    path('v1/metrics/', rag_metrics, name='metrics'),
    path('v1/clear/cache/', clear_cache, name='clear-cache'),
    path('v1/status/', system_status, name='system-status'),
]

"""
COMPLETE URL STRUCTURE:
=======================

BASE: /api/rag/

CHAT ENDPOINTS (VectorStoreRAGChatViewSet):
1. POST   /api/rag/chat/query/                  # Main chat query
2. GET    /api/rag/chat/history/                # Get chat history  
3. DELETE /api/rag/chat/clear_history/          # Clear history
4. POST   /api/rag/chat/diagnose/               # Diagnose query
5. GET    /api/rag/chat/vectorstore_stats/      # Vector store stats
6. POST   /api/rag/chat/test_vector_search/     # Test vector search

DOCUMENT ENDPOINTS (ModelViewSet):
7. GET    /api/rag/documents/                   # List all documents
8. POST   /api/rag/documents/                   # Upload document
9. GET    /api/rag/documents/{id}/              # Get single document
10. PUT   /api/rag/documents/{id}/              # Update document
11. PATCH /api/rag/documents/{id}/              # Partial update
12. DELETE /api/rag/documents/{id}/             # Delete document

UTILITY ENDPOINTS (API Views):
13. POST   /api/rag/v1/initialize/              # Initialize vector store
14. GET    /api/rag/v1/metrics/                 # Get system metrics
15. DELETE /api/rag/v1/clear/cache/             # Clear cache
16. GET    /api/rag/v1/status/                  # System status

TOTAL: 16 Endpoints
"""