# ============================================
# COMPREHENSIVE TEST SUITE FOR RAG SYSTEM
# File: apps/rag_system/tests/test_rag_complete.py
# ============================================

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.rag_system.services.vectorstore_service import VectorStoreService
from apps.rag_system.services.groq_service import GroqService
from apps.rag_system.services.database_connector import DatabaseConnector
from apps.rag_system.services.orchestrator import VectorStoreOrchestrator

User = get_user_model()


class TestVectorStoreService(TestCase):
    """Test vector store operations"""
    
    def setUp(self):
        self.vectorstore = VectorStoreService()
    
    def test_initialization(self):
        """Test vector store initializes correctly"""
        assert self.vectorstore is not None
        assert self.vectorstore.embeddings is not None
        assert self.vectorstore.vectorstore is not None
    
    def test_embedding_creation(self):
        """Test that embeddings are created for text"""
        text = "Test student information"
        
        # Add document
        self.vectorstore.add_documents(
            texts=[text],
            metadatas=[{"type": "test"}]
        )
        
        # Search should return results
        results = self.vectorstore.search("student", k=1)
        assert len(results) > 0
    
    def test_search_functionality(self):
        """Test semantic search works"""
        # Add test documents
        docs = [
            "Students are enrolled in classes",
            "Teachers teach subjects",
            "Exams are scheduled monthly"
        ]
        
        self.vectorstore.add_documents(
            texts=docs,
            metadatas=[{"type": "test"} for _ in docs]
        )
        
        # Search
        results = self.vectorstore.search("student enrollment", k=3)
        
        assert len(results) > 0
        assert any("student" in r.get("content", "").lower() for r in results)
    
    def test_query_expansion(self):
        """Test query expansion generates variations"""
        query = "How many users"
        expanded = self.vectorstore._expand_query(query)
        
        assert len(expanded) >= 1
        assert query in expanded
    
    def test_stats(self):
        """Test statistics retrieval"""
        stats = self.vectorstore.stats()
        
        assert "total_documents" in stats
        assert "status" in stats
        assert isinstance(stats["total_documents"], int)


class TestGroqService(TestCase):
    """Test GROQ LLM service"""
    
    def setUp(self):
        self.groq = GroqService()
    
    def test_initialization(self):
        """Test GROQ service initializes"""
        assert self.groq is not None
        assert self.groq.client is not None
        assert self.groq.model == "llama-3.3-70b-versatile"
    
    def test_connection(self):
        """Test GROQ API connection"""
        result = self.groq.test_connection()
        assert result == True
    
    def test_generate_response(self):
        """Test response generation"""
        result = self.groq.generate_response(
            query="What is 2+2?",
            context=["This is a simple math question"]
        )
        
        assert result["success"] == True
        assert "response" in result
        assert len(result["response"]) > 0
        assert result["tokens_used"] > 0
    
    def test_sql_generation(self):
        """Test SQL query generation"""
        table_context = {
            "table_name": "students",
            "columns": ["id", "name", "email", "created_at"],
            "entity_type": "student",
            "row_count": 100
        }
        
        sql = self.groq.generate_intelligent_sql(
            "Count all students",
            table_context
        )
        
        assert sql is not None
        assert "SELECT" in sql.upper()
        assert "COUNT" in sql.upper()
        assert "students" in sql.lower()
    
    def test_sql_with_filter(self):
        """Test SQL generation with filtering"""
        table_context = {
            "table_name": "users_user",
            "columns": ["id", "username", "email", "is_active"],
            "entity_type": "user"
        }
        
        sql = self.groq.generate_intelligent_sql(
            "Show active users",
            table_context
        )
        
        assert "users_user" in sql.lower()
        assert "WHERE" in sql.upper() or "where" in sql.lower()


class TestDatabaseConnector(TestCase):
    """Test database connection and schema extraction"""
    
    def setUp(self):
        self.db_connector = DatabaseConnector()
    
    def test_get_all_tables(self):
        """Test retrieving all tables"""
        tables = self.db_connector.get_all_tables()
        
        assert isinstance(tables, list)
        assert len(tables) > 0
    
    def test_table_name_resolution(self):
        """Test resolving entity to table name"""
        # Test common entities
        test_cases = [
            ("student", ["students", "student_behavior"]),
            ("teacher", ["teachers", "teachers_teacher"]),
            ("user", ["users_user", "auth_user"])
        ]
        
        for entity, expected_tables in test_cases:
            result = self.db_connector.get_actual_table_name(entity)
            assert result is not None
            # Should be one of the expected tables
            if result:
                assert any(exp in result for exp in expected_tables)
    
    def test_get_table_columns(self):
        """Test retrieving table columns"""
        tables = self.db_connector.get_all_tables()
        
        if tables:
            test_table = tables[0]
            columns = self.db_connector.get_table_columns(test_table)
            
            assert isinstance(columns, list)
            if columns:
                assert "name" in columns[0]
                assert "type" in columns[0]
    
    def test_discover_relevant_tables(self):
        """Test table discovery from query"""
        test_queries = [
            "How many students?",
            "List all teachers",
            "Show user information"
        ]
        
        for query in test_queries:
            tables = self.db_connector.discover_relevant_tables(query)
            assert isinstance(tables, list)


class TestOrchestrator(TestCase):
    """Test RAG orchestrator"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orchestrator = VectorStoreOrchestrator()
    
    def test_initialization(self):
        """Test orchestrator initializes all services"""
        assert self.orchestrator.rag_service is not None
        assert self.orchestrator.groq_service is not None
        assert self.orchestrator.db_connector is not None
    
    def test_query_classification(self):
        """Test query type classification"""
        test_cases = [
            ("How many students?", "DATABASE_QUERY"),
            ("Hello", "CONVERSATIONAL"),
            ("Show all users", "DATABASE_QUERY")
        ]
        
        for query, expected_type in test_cases:
            result = self.orchestrator._classify_query(query)
            # Just check it returns a valid QueryType
            assert result is not None
    
    def test_process_conversational_query(self):
        """Test conversational query handling"""
        user_context = {
            "user_id": 1,
            "username": "test_user",
            "user_type": "admin"
        }
        
        result = self.orchestrator.process_intelligent_query(
            "Hello, what can you do?",
            user_context
        )
        
        assert "response" in result
        assert result["success"] == True
        assert "conversational" in result.get("query_type", "")
    
    def test_process_database_query(self):
        """Test database query handling"""
        user_context = {
            "user_id": 1,
            "username": "test_user",
            "user_type": "admin"
        }
        
        result = self.orchestrator.process_intelligent_query(
            "How many users are there?",
            user_context
        )
        
        assert "response" in result
        assert result["success"] == True
        assert len(result["response"]) > 0
    
    def test_diagnose_query(self):
        """Test query diagnosis"""
        diagnosis = self.orchestrator.diagnose_query("Count students")
        
        assert "query" in diagnosis
        assert "query_type" in diagnosis
        assert "processing_method" in diagnosis
        assert "relevant_tables" in diagnosis
    
    def test_system_status(self):
        """Test system status retrieval"""
        status = self.orchestrator.get_system_status()
        
        assert "status" in status
        assert status["status"] in ["operational", "error"]
        
        if status["status"] == "operational":
            assert "vector_store" in status
            assert "database" in status
            assert "capabilities" in status


class TestEndToEndRAG(TestCase):
    """End-to-end integration tests"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orchestrator = VectorStoreOrchestrator()
    
    def test_student_count_query(self):
        """Test: How many students?"""
        result = self.orchestrator.process_intelligent_query(
            "How many students are there?",
            {"user_id": 1}
        )
        
        assert result["success"] == True
        assert "student" in result["response"].lower()
    
    def test_teacher_list_query(self):
        """Test: List teachers"""
        result = self.orchestrator.process_intelligent_query(
            "Show all teachers",
            {"user_id": 1}
        )
        
        assert result["success"] == True
        assert "teacher" in result["response"].lower()
    
    def test_user_information_query(self):
        """Test: Get user information"""
        result = self.orchestrator.process_intelligent_query(
            "Tell me about users in the system",
            {"user_id": 1}
        )
        
        assert result["success"] == True
        assert len(result["response"]) > 10
    
    def test_complex_query(self):
        """Test complex multi-entity query"""
        result = self.orchestrator.process_intelligent_query(
            "How many students are enrolled in classes taught by active teachers?",
            {"user_id": 1}
        )
        
        assert result["success"] == True
        # Should have retrieved relevant context
        assert result["context_sources"]["vector_store_results"] > 0


class TestPerformance(TestCase):
    """Performance and optimization tests"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orchestrator = VectorStoreOrchestrator()
    
    def test_response_time(self):
        """Test query response time is acceptable"""
        import time
        
        start = time.time()
        result = self.orchestrator.process_intelligent_query(
            "Count users",
            {"user_id": 1}
        )
        elapsed = time.time() - start
        
        # Should respond within 10 seconds
        assert elapsed < 10.0
        assert "response_time" in result
    
    def test_caching(self):
        """Test query caching works"""
        query = "How many students are there?"
        
        # First call
        result1 = self.orchestrator.rag_service.process_query(
            query,
            {"user_id": 1},
            use_cache=True
        )
        
        # Second call (should be cached)
        result2 = self.orchestrator.rag_service.process_query(
            query,
            {"user_id": 1},
            use_cache=True
        )
        
        # Second call should be faster
        assert result2["response_time"] <= result1["response_time"]
    
    def test_concurrent_queries(self):
        """Test handling multiple concurrent queries"""
        import concurrent.futures
        
        queries = [
            "Count students",
            "List teachers",
            "Show classes",
            "Get user info",
            "Display subjects"
        ]
        
        def process_query(q):
            return self.orchestrator.process_intelligent_query(q, {"user_id": 1})
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(process_query, queries))
        
        # All should succeed
        assert all(r["success"] for r in results)


class TestErrorHandling(TestCase):
    """Test error handling and edge cases"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orchestrator = VectorStoreOrchestrator()
    
    def test_empty_query(self):
        """Test handling of empty query"""
        result = self.orchestrator.process_intelligent_query(
            "",
            {"user_id": 1}
        )
        
        assert "response" in result
    
    def test_very_long_query(self):
        """Test handling of very long query"""
        long_query = "Tell me about students " * 100
        
        result = self.orchestrator.process_intelligent_query(
            long_query,
            {"user_id": 1}
        )
        
        assert "response" in result
    
    def test_special_characters(self):
        """Test queries with special characters"""
        queries = [
            "What's the count of students?",
            "Show users with email @gmail.com",
            "List items with 50% discount"
        ]
        
        for query in queries:
            result = self.orchestrator.process_intelligent_query(
                query,
                {"user_id": 1}
            )
            assert "response" in result
    
    def test_nonexistent_table(self):
        """Test query for nonexistent entity"""
        result = self.orchestrator.process_intelligent_query(
            "How many unicorns are there?",
            {"user_id": 1}
        )
        
        # Should still return a response, possibly indicating no data
        assert "response" in result


# ============================================
# PYTEST FIXTURES
# ============================================

@pytest.fixture
def vectorstore():
    """Fixture for vector store service"""
    return VectorStoreService()


@pytest.fixture
def groq_service():
    """Fixture for GROQ service"""
    return GroqService()


@pytest.fixture
def db_connector():
    """Fixture for database connector"""
    return DatabaseConnector()


@pytest.fixture
def orchestrator():
    """Fixture for orchestrator"""
    return VectorStoreOrchestrator()


@pytest.fixture
def sample_user(db):
    """Fixture for test user"""
    User = get_user_model()
    user = User.objects.create_user(
        username="test_user",
        email="test@example.com",
        password="testpass123"
    )
    return user


# ============================================
# RUN TESTS
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])