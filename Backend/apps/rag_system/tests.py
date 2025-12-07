from django.test import TestCase

# Create your tests here.

# ============================================
# FILE 23: apps/rag_system/tests.py
# ============================================

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics
from .services.rag_service import RAGService
from .utils import (
    validate_sql_query, sanitize_sql_query, 
    calculate_similarity_score, create_query_hash
)

User = get_user_model()


class RAGModelsTestCase(TestCase):
    """Test RAG models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_document_store_creation(self):
        """Test DocumentStore model creation"""
        doc = DocumentStore.objects.create(
            title='Test Document',
            document_type='pdf',
            uploaded_by=self.user
        )
        self.assertEqual(doc.title, 'Test Document')
        self.assertFalse(doc.is_processed)
    
    def test_chat_history_creation(self):
        """Test ChatHistory model creation"""
        chat = ChatHistory.objects.create(
            user=self.user,
            session_id='test-session',
            query='Test query',
            response='Test response'
        )
        self.assertEqual(chat.query, 'Test query')
        self.assertEqual(chat.tokens_used, 0)
    
    def test_query_cache_creation(self):
        """Test QueryCache model creation"""
        query_hash = create_query_hash('test query')
        cache = QueryCache.objects.create(
            query_hash=query_hash,
            query_text='test query',
            response='cached response'
        )
        self.assertEqual(cache.hit_count, 0)


class RAGUtilsTestCase(TestCase):
    """Test RAG utilities"""
    
    def test_validate_sql_query(self):
        """Test SQL query validation"""
        # Valid query
        self.assertTrue(validate_sql_query('SELECT * FROM students'))
        
        # Invalid queries
        self.assertFalse(validate_sql_query('DROP TABLE students'))
        self.assertFalse(validate_sql_query('DELETE FROM students'))
        self.assertFalse(validate_sql_query('UPDATE students SET name="test"'))
    
    def test_sanitize_sql_query(self):
        """Test SQL query sanitization"""
        query = 'SELECT * FROM students -- comment'
        sanitized = sanitize_sql_query(query)
        self.assertNotIn('--', sanitized)
    
    def test_similarity_score(self):
        """Test similarity score calculation"""
        score = calculate_similarity_score('hello world', 'hello world')
        self.assertEqual(score, 1.0)
        
        score = calculate_similarity_score('hello', 'world')
        self.assertEqual(score, 0.0)
    
    def test_create_query_hash(self):
        """Test query hash creation"""
        hash1 = create_query_hash('test query')
        hash2 = create_query_hash('test query')
        self.assertEqual(hash1, hash2)
        
        hash3 = create_query_hash('different query')
        self.assertNotEqual(hash1, hash3)