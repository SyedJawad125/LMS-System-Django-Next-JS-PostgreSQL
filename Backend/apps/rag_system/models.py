from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class DocumentStore(models.Model):
    """Store uploaded documents for RAG"""
    DOCUMENT_TYPES = (
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('csv', 'CSV File'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='rag_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    vector_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'rag_document_store'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title


class ChatHistory(models.Model):
    """Store chat conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rag_chats')
    session_id = models.CharField(max_length=100, db_index=True)
    query = models.TextField()
    response = models.TextField()
    context_used = models.JSONField(default=list, blank=True)
    sql_queries = models.JSONField(default=list, blank=True)
    tokens_used = models.IntegerField(default=0)
    response_time = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rag_chat_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.query[:50]}"


class QueryCache(models.Model):
    """Cache frequent queries"""
    query_hash = models.CharField(max_length=64, unique=True, db_index=True)
    query_text = models.TextField()
    response = models.TextField()
    context = models.JSONField(default=dict)
    hit_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rag_query_cache'
        ordering = ['-hit_count']
    
    def __str__(self):
        return f"{self.query_text[:50]} (hits: {self.hit_count})"


class RAGMetrics(models.Model):
    """Track RAG system performance"""
    date = models.DateField(auto_now_add=True, unique=True)
    total_queries = models.IntegerField(default=0)
    successful_queries = models.IntegerField(default=0)
    failed_queries = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0.0)
    total_tokens_used = models.IntegerField(default=0)
    cache_hit_rate = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'rag_metrics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Metrics for {self.date}"