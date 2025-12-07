from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics
from .serializers import (
    DocumentStoreSerializer, ChatQuerySerializer, 
    ChatHistorySerializer, RAGMetricsSerializer
)
from .services.orchestrator import RAGOrchestrator
from .services.rag_service import RAGService
from .services.pdf_reader import DocumentReader
import uuid


class RAGChatViewSet(viewsets.ViewSet):
    """RAG Chat API ViewSet"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = None
    
    def _get_orchestrator(self):
        """Lazy initialization of orchestrator"""
        if self.orchestrator is None:
            self.orchestrator = RAGOrchestrator()
        return self.orchestrator
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        Process user query with RAG
        
        POST /api/rag/chat/query/
        Body: {
            "query": "How many students are in Grade 10?",
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
        
        # Process query
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
                sql_queries=result.get('sql_query', []),
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
        
        queryset = queryset[:limit]
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


class DocumentManagementViewSet(viewsets.ModelViewSet):
    """Document Management ViewSet"""
    queryset = DocumentStore.objects.all()
    serializer_class = DocumentStoreSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Upload and process document"""
        document = serializer.save(uploaded_by=self.request.user)
        
        # Process document immediately (or use Celery in production)
        try:
            self._process_document(document)
        except Exception as e:
            print(f"Error processing document: {e}")
    
    def _process_document(self, document):
        """Process document and add to vector store"""
        try:
            # Read document
            file_path = document.file.path
            doc_reader = DocumentReader()
            text = doc_reader.read_document(file_path, document.document_type)
            
            if text:
                # Add to vector store
                rag_service = RAGService()
                rag_service.vectorstore.add_documents(
                    texts=[text],
                    metadatas=[{
                        'document_id': str(document.id),
                        'title': document.title,
                        'type': document.document_type
                    }]
                )
                
                document.is_processed = True
                document.vector_count = len(text.split('\n\n'))
                document.save()
                print(f"Document {document.title} processed successfully")
        except Exception as e:
            print(f"Error processing document: {e}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def index_database_tables(request):
    """
    Index database tables into vector store
    
    POST /api/rag/index-database/
    Body: {"tables": ["students", "teachers"]} or {"tables": null} for all
    """
    table_names = request.data.get('tables', None)
    
    try:
        rag_service = RAGService()
        rag_service.index_database_tables(table_names)
        
        return Response(
            {"message": "Database tables indexed successfully"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
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
    
    # Calculate totals
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
