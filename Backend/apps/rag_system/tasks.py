from celery import shared_task


@shared_task
def process_document_task(document_id: str):
    """Process document asynchronously"""
    from .models import DocumentStore
    from .services.rag_service import RAGService
    from .services.pdf_reader import DocumentReader
    
    try:
        document = DocumentStore.objects.get(id=document_id)
        
        # Read document
        doc_reader = DocumentReader()
        text = doc_reader.read_document(document.file.path, document.document_type)
        
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
            
            return f"Document {document_id} processed successfully"
        else:
            return f"Could not extract text from document {document_id}"
            
    except Exception as e:
        return f"Error processing document {document_id}: {str(e)}"


@shared_task
def index_all_database_tables():
    """Index all important database tables"""
    from .services.rag_service import RAGService
    
    rag_service = RAGService()
    rag_service.index_database_tables()
    return "Database tables indexed successfully"


@shared_task
def cleanup_old_cache():
    """Clean up old cache entries"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import QueryCache
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    deleted_count = QueryCache.objects.filter(
        last_used__lt=thirty_days_ago
    ).delete()[0]
    
    return f"Deleted {deleted_count} old cache entries"