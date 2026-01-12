# ============================================
# ENHANCED VIEWS
# File: apps/rag_system/views.py
# ============================================

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics
from .serializers import (
    DocumentStoreSerializer, ChatQuerySerializer, 
    ChatHistorySerializer, RAGMetricsSerializer
)
from .services.orchestrator import VectorStoreOrchestrator
from .services.rag_service import VectorStoreRAGService
from .services.vectorstore_service import VectorStoreService
from .services.database_connector import DatabaseConnector
import uuid


class VectorStoreRAGChatViewSet(viewsets.ViewSet):
    """Enhanced Vector Store + PostgreSQL RAG Chat API"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = None
        self.vectorstore = None
        self.db_connector = None
    
    def _get_orchestrator(self):
        """Lazy initialization of orchestrator"""
        if self.orchestrator is None:
            self.orchestrator = VectorStoreOrchestrator()
        return self.orchestrator
    
    def _get_vectorstore(self):
        """Lazy initialization of vector store"""
        if self.vectorstore is None:
            self.vectorstore = VectorStoreService()
        return self.vectorstore
    
    def _get_db_connector(self):
        """Lazy initialization of database connector"""
        if self.db_connector is None:
            self.db_connector = DatabaseConnector()
        return self.db_connector
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        Process user query with Enhanced RAG
        
        POST /api/rag/chat/query/
        Body: {
            "query": "How many users are there?",
            "session_id": "optional-session-id",
            "use_cache": true
        }
        """
        serializer = ChatQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request", "details": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        query = serializer.validated_data['query']
        session_id = serializer.validated_data.get('session_id', str(uuid.uuid4()))
        use_cache = serializer.validated_data.get('use_cache', True)
        
        # Build user context
        user_context = {
            'user_id': request.user.id,
            'user_type': getattr(request.user, 'user_type', 'user'),
            'username': request.user.username
        }
        
        try:
            orchestrator = self._get_orchestrator()
            result = orchestrator.process_intelligent_query(query, user_context)
            
            # Save to chat history
            ChatHistory.objects.create(
                user=request.user,
                session_id=session_id,
                query=query,
                response=result.get('response', ''),
                context_used=result.get('context_sources', {}),
                tokens_used=result.get('tokens_used', 0),
                response_time=result.get('response_time', 0.0)
            )
            
            # Update metrics
            self._update_metrics(result)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            return Response(
                {
                    "error": str(e), 
                    "success": False,
                    "response": "Sorry, I encountered an error processing your request."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get chat history for current user
        
        GET /api/rag/chat/history/?session_id=xxx&limit=50
        """
        session_id = request.query_params.get('session_id')
        limit = int(request.query_params.get('limit', 50))
        
        queryset = ChatHistory.objects.filter(user=request.user)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        queryset = queryset.order_by('-created_at')[:limit]
        serializer = ChatHistorySerializer(queryset, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        """Clear chat history"""
        session_id = request.query_params.get('session_id')
        
        if session_id:
            count = ChatHistory.objects.filter(
                user=request.user, 
                session_id=session_id
            ).delete()[0]
        else:
            count = ChatHistory.objects.filter(user=request.user).delete()[0]
        
        return Response(
            {"message": f"Cleared {count} chat messages"}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def diagnose(self, request):
        """
        Diagnose a query without executing it
        
        POST /api/rag/chat/diagnose/
        Body: {"query": "How many users?"}
        """
        query = request.data.get('query', '')
        
        if not query:
            return Response(
                {"error": "Query parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            orchestrator = self._get_orchestrator()
            diagnosis = orchestrator.diagnose_query(query)
            
            return Response(diagnosis, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def vectorstore_stats(self, request):
        """
        Get vector store statistics
        
        GET /api/rag/chat/vectorstore_stats/
        """
        try:
            vectorstore = self._get_vectorstore()
            stats = vectorstore.stats()
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def database_summary(self, request):
        """
        Get database summary
        
        GET /api/rag/chat/database_summary/
        """
        try:
            db_connector = self._get_db_connector()
            
            all_tables = db_connector.get_all_tables()
            user_tables = [t for t in all_tables if not any(
                skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']
            )]
            
            # Get sample table info
            sample_tables = {}
            for table in user_tables[:10]:
                try:
                    info = db_connector.get_table_schema_info(table)
                    sample_tables[table] = {
                        "columns": info.get("columns", [])[:5],
                        "row_count": info.get("row_count", 0),
                        "entity_type": info.get("entity_type", "unknown")
                    }
                except:
                    pass
            
            return Response({
                "total_tables": len(all_tables),
                "user_tables": len(user_tables),
                "sample_tables": sample_tables,
                "all_table_names": user_tables[:30]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test_vector_search(self, request):
        """
        Test vector store search directly
        
        POST /api/rag/chat/test_vector_search/
        Body: {"query": "users", "k": 5}
        """
        query = request.data.get('query', '')
        k = int(request.data.get('k', 5))
        
        if not query:
            return Response(
                {"error": "Query parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vectorstore = self._get_vectorstore()
            results = vectorstore.search(query, k=k)
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append({
                    "rank": i,
                    "score": round(result.get('score', 0), 3),
                    "type": result.get('metadata', {}).get('type', 'unknown'),
                    "entity": result.get('metadata', {}).get('entity', 'unknown'),
                    "table": result.get('metadata', {}).get('table_name', 'N/A'),
                    "content_preview": result.get('content', '')[:200] + "..."
                })
            
            return Response({
                "query": query,
                "results_count": len(results),
                "results": formatted_results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _update_metrics(self, result: dict):
        """Update RAG metrics"""
        from django.utils import timezone
        
        today = timezone.now().date()
        metrics, created = RAGMetrics.objects.get_or_create(date=today)
        
        metrics.total_queries += 1
        if result.get('success'):
            metrics.successful_queries += 1
        else:
            metrics.failed_queries += 1
        
        # Update average response time
        total = metrics.total_queries
        current_avg = metrics.avg_response_time
        new_time = result.get('response_time', 0)
        metrics.avg_response_time = ((current_avg * (total - 1)) + new_time) / total
        
        metrics.total_tokens_used += result.get('tokens_used', 0)
        metrics.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_vectorstore(request):
    """
    Initialize vector store with database knowledge
    
    POST /api/rag/v1/initialize/
    Body: {"refresh": false}
    """
    try:
        refresh = request.data.get('refresh', False)
        
        vectorstore = VectorStoreService()
        vectorstore.initialize_with_database_knowledge(refresh=refresh)
        
        stats = vectorstore.stats()
        
        return Response({
            "message": "Vector store initialized successfully",
            "stats": stats,
            "refreshed": refresh
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rag_metrics(request):
    """Get RAG system metrics"""
    from django.utils import timezone
    from datetime import timedelta
    
    days = int(request.query_params.get('days', 7))
    start_date = timezone.now().date() - timedelta(days=days)
    
    metrics = RAGMetrics.objects.filter(date__gte=start_date).order_by('-date')
    serializer = RAGMetricsSerializer(metrics, many=True)
    
    total_data = {
        'total_queries': sum(m.total_queries for m in metrics),
        'successful_queries': sum(m.successful_queries for m in metrics),
        'failed_queries': sum(m.failed_queries for m in metrics),
        'avg_response_time': sum(m.avg_response_time for m in metrics) / len(metrics) if metrics else 0,
        'total_tokens': sum(m.total_tokens_used for m in metrics),
        'daily_metrics': serializer.data
    }
    
    return Response(total_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    """Clear query cache"""
    count = QueryCache.objects.all().delete()[0]
    return Response(
        {"message": f"Cleared {count} cached queries"},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_status(request):
    """Get complete system status"""
    try:
        orchestrator = VectorStoreOrchestrator()
        status_info = orchestrator.get_system_status()
        
        from django.utils import timezone
        status_info["timestamp"] = timezone.now().isoformat()
        status_info["endpoints"] = {
            "chat_query": "/api/rag/chat/query/",
            "chat_history": "/api/rag/chat/history/",
            "diagnose_query": "/api/rag/chat/diagnose/",
            "vectorstore_stats": "/api/rag/chat/vectorstore_stats/",
            "database_summary": "/api/rag/chat/database_summary/",
            "test_search": "/api/rag/chat/test_vector_search/",
            "initialize": "/api/rag/v1/initialize/",
            "metrics": "/api/rag/v1/metrics/",
            "clear_cache": "/api/rag/v1/clear/cache/",
            "system_status": "/api/rag/v1/status/"
        }
        
        return Response(status_info, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {
                "system": "Enhanced Vector Store + PostgreSQL RAG",
                "status": "error",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
# Add this class definition in views.py
class DocumentManagementViewSet(viewsets.ModelViewSet):
    """Document management for RAG system"""
    permission_classes = [IsAuthenticated]
    queryset = DocumentStore.objects.all()
    serializer_class = DocumentStoreSerializer
    
    def get_queryset(self):
        """Return only user's documents"""
        return DocumentStore.objects.filter(uploaded_by=self.request.user)
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user"""
        serializer.save(uploaded_by=self.request.user)