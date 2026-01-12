# ============================================
# FINAL ENHANCED ORCHESTRATOR
# File: apps/rag_system/services/orchestrator.py
# ============================================

from typing import Dict, List
from enum import Enum
from .rag_service import VectorStoreRAGService
from .groq_service import GroqService
from .database_connector import DatabaseConnector


class QueryType(Enum):
    """Types of queries"""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    PROCEDURAL = "procedural"
    COLUMN_QUERY = "column_query"
    DATABASE_QUERY = "database_query"


class VectorStoreOrchestrator:
    """Enhanced Orchestrator for Vector Store + PostgreSQL RAG"""
    
    def __init__(self):
        print("🚀 Initializing Enhanced Orchestrator...")
        self.rag_service = VectorStoreRAGService()
        self.groq_service = GroqService()
        self.db_connector = DatabaseConnector()
        print("✅ Enhanced Orchestrator ready!")
    
    def process_intelligent_query(self, query: str, user_context: Dict) -> Dict:
        """Intelligently process query using vector store + database"""
        
        # Step 1: Classify query type
        query_type = self._classify_query(query)
        print(f"🔍 Query '{query}' classified as: {query_type.value}")
        
        # Step 2: Route to appropriate handler
        if query_type == QueryType.CONVERSATIONAL:
            return self._handle_conversational_query(query, user_context)
        elif query_type == QueryType.DATABASE_QUERY:
            return self._handle_database_query(query, user_context)
        else:
            # All other queries use the enhanced RAG service
            return self.rag_service.process_query(query, user_context, use_cache=True)
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query type using keywords"""
        query_lower = query.lower()
        
        # Conversational queries
        conversational_keywords = [
            'hello', 'hi', 'hey', 'thanks', 'thank you',
            'good morning', 'good afternoon', 'what can you do',
            'help', 'who are you', 'how are you'
        ]
        if any(kw in query_lower for kw in conversational_keywords):
            return QueryType.CONVERSATIONAL
        
        # Database-specific queries
        database_keywords = [
            'how many', 'count', 'total', 'number of',
            'show', 'list', 'display', 'get', 'find'
        ]
        lms_entities = [
            'user', 'student', 'teacher', 'parent', 'role',
            'class', 'subject', 'exam', 'fee', 'attendance',
            'vehicle', 'route', 'employee', 'assignment', 'leave'
        ]
        
        has_database_keyword = any(kw in query_lower for kw in database_keywords)
        has_entity = any(entity in query_lower for entity in lms_entities)
        
        if has_database_keyword and has_entity:
            return QueryType.DATABASE_QUERY
        
        # Column-specific queries
        if any(word in query_lower for word in ['with', 'where', 'having', 'by']):
            return QueryType.COLUMN_QUERY
        
        # Analytical queries
        if any(word in query_lower for word in ['how many', 'count', 'total', 'average']):
            return QueryType.ANALYTICAL
        
        # Procedural queries
        if any(kw in query_lower for kw in ['how to', 'how do i', 'steps', 'guide']):
            return QueryType.PROCEDURAL
        
        # Default: Factual query
        return QueryType.FACTUAL
    
    def _handle_conversational_query(self, query: str, user_context: Dict) -> Dict:
        """Handle general conversation"""
        print(f"💬 Handling conversational query")
        
        system_prompt = f"""You are a helpful LMS assistant.
User: {user_context.get('username', 'User')} ({user_context.get('user_type', 'user')})

CAPABILITIES:
- Answer questions about users, students, teachers, classes, exams, fees, attendance
- Provide information from the LMS database
- Help with queries about academic and operational data

Be friendly, conversational, and helpful. Suggest specific queries if needed.

Example responses:
- "Hello! I can help you find information about the LMS system. Try asking questions like 'How many students?' or 'Show all teachers'"
- "I can help you with queries about users, students, teachers, classes, exams, fees, and more!"
"""
        
        response = self.groq_service.generate_response(query, [], system_prompt)
        
        return {
            "query": query,
            "response": response['response'],
            "query_type": "conversational",
            "tokens_used": response.get('tokens_used', 0),
            "success": response.get('success', False),
            "context_sources": {"response_method": "conversational"},
            "response_time": 0.0
        }
    
    def _handle_database_query(self, query: str, user_context: Dict) -> Dict:
        """Handle database-specific queries"""
        print(f"🗄️ Handling database query")
        
        # Use the enhanced RAG service which has database integration
        return self.rag_service.process_query(query, user_context, use_cache=False)
    
    def diagnose_query(self, query: str) -> Dict:
        """Diagnose how a query will be processed"""
        query_type = self._classify_query(query)
        
        # Get database context
        relevant_tables = self.db_connector.discover_relevant_tables(query)
        
        # Get enhancement suggestions
        enhancements = self._get_query_enhancements(query)
        
        return {
            "query": query,
            "query_type": query_type.value,
            "description": self._get_query_type_description(query_type),
            "processing_method": "vector_store_with_database",
            "relevant_tables": relevant_tables,
            "recommended_enhancements": enhancements,
            "will_use_vector_store": True,
            "will_use_database": query_type in [QueryType.DATABASE_QUERY, QueryType.ANALYTICAL]
        }
    
    def _get_query_type_description(self, query_type: QueryType) -> str:
        """Get description for query type"""
        descriptions = {
            QueryType.FACTUAL: "Factual query requesting specific information",
            QueryType.ANALYTICAL: "Analytical query for counts, totals, or statistics",
            QueryType.COLUMN_QUERY: "Query filtering by specific columns/attributes",
            QueryType.CONVERSATIONAL: "General conversation or greetings",
            QueryType.PROCEDURAL: "How-to or procedural guidance",
            QueryType.DATABASE_QUERY: "Direct database query for LMS entities"
        }
        return descriptions.get(query_type, "General query")
    
    def _get_query_enhancements(self, query: str) -> List[str]:
        """Get recommended query enhancements"""
        query_lower = query.lower()
        enhancements = []
        
        if "how many" in query_lower or "count" in query_lower:
            enhancements.extend([
                "Add specific entity: 'How many [users/students/teachers]?'",
                "Add time filter: 'How many users created this month?'",
                "Add status filter: 'How many active students?'"
            ])
        
        if "show" in query_lower or "list" in query_lower:
            enhancements.extend([
                "Be specific: 'Show [all/active/recent] [entity]s'",
                "Add sorting: 'List users by name'",
                "Add limit: 'Show top 10 students'"
            ])
        
        if "with" in query_lower or "where" in query_lower:
            enhancements.extend([
                "Specify exact values: 'Users with email containing @gmail'",
                "Use comparisons: 'Students with attendance > 90%'",
                "Combine filters: 'Teachers in Math department'"
            ])
        
        return enhancements
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        try:
            # Vector store status
            vectorstore_stats = self.rag_service.vectorstore.stats()
            
            # Database status
            db_summary = self.rag_service.get_database_summary()
            
            return {
                "status": "operational",
                "vector_store": vectorstore_stats,
                "database": db_summary,
                "capabilities": {
                    "conversational": True,
                    "database_queries": True,
                    "vector_search": True,
                    "entity_extraction": True,
                    "query_diagnosis": True
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }