# from typing import Dict
# from enum import Enum
# from .rag_service import RAGService
# from .groq_service import GroqService


# class QueryType(Enum):
#     """Types of queries"""
#     FACTUAL = "factual"  # Simple database lookup
#     ANALYTICAL = "analytical"  # Requires computation
#     CONVERSATIONAL = "conversational"  # General chat
#     PROCEDURAL = "procedural"  # How-to questions


# class RAGOrchestrator:
#     """Orchestrate RAG workflow with intelligence"""
    
#     def __init__(self):
#         print("Initializing RAG Orchestrator...")
#         self.rag_service = RAGService()
#         self.groq_service = GroqService()
#         print("RAG Orchestrator ready!")
    
#     def process_intelligent_query(self, query: str, user_context: Dict) -> Dict:
#         """Intelligently process query based on type"""
        
#         # Step 1: Classify query type
#         query_type = self._classify_query(query)
#         print(f"Query classified as: {query_type.value}")
        
#         # Step 2: Route to appropriate handler
#         if query_type == QueryType.FACTUAL:
#             return self._handle_factual_query(query, user_context)
#         elif query_type == QueryType.ANALYTICAL:
#             return self._handle_analytical_query(query, user_context)
#         elif query_type == QueryType.CONVERSATIONAL:
#             return self._handle_conversational_query(query, user_context)
#         else:
#             return self._handle_procedural_query(query, user_context)
    
#     def _classify_query(self, query: str) -> QueryType:
#         """Classify query type using keywords"""
#         query_lower = query.lower()
        
#         # Check for analytical queries
#         analytical_keywords = [
#             'how many', 'count', 'calculate', 'average', 'total', 
#             'sum', 'compare', 'percentage', 'ratio'
#         ]
#         if any(kw in query_lower for kw in analytical_keywords):
#             return QueryType.ANALYTICAL
        
#         # Check for factual queries
#         factual_keywords = [
#             'what is', 'who is', 'when', 'where', 'show me', 
#             'get', 'list', 'find', 'display'
#         ]
#         if any(kw in query_lower for kw in factual_keywords):
#             return QueryType.FACTUAL
        
#         # Check for procedural queries
#         procedural_keywords = [
#             'how to', 'how do i', 'how can i', 'steps', 
#             'guide', 'tutorial', 'procedure'
#         ]
#         if any(kw in query_lower for kw in procedural_keywords):
#             return QueryType.PROCEDURAL
        
#         # Default to conversational
#         return QueryType.CONVERSATIONAL
    
#     def _handle_factual_query(self, query: str, user_context: Dict) -> Dict:
#         """Handle factual queries - direct database lookups"""
#         result = self.rag_service.process_query(query, user_context, use_cache=True)
#         result['query_type'] = 'factual'
#         return result
    
#     def _handle_analytical_query(self, query: str, user_context: Dict) -> Dict:
#         """Handle analytical queries - require computation"""
#         result = self.rag_service.process_query(query, user_context, use_cache=False)
#         result['query_type'] = 'analytical'
#         return result
    
#     def _handle_conversational_query(self, query: str, user_context: Dict) -> Dict:
#         """Handle general conversation"""
#         system_prompt = f"""You are a helpful LMS assistant. 
# User info: {user_context.get('username', 'User')} ({user_context.get('user_type', 'user')})
# Be friendly, conversational, and helpful."""
        
#         response = self.groq_service.generate_response(query, [], system_prompt)
        
#         return {
#             "query": query,
#             "response": response['response'],
#             "query_type": "conversational",
#             "tokens_used": response.get('tokens_used', 0),
#             "success": response.get('success', False),
#             "context_sources": {},
#             "response_time": 0.0
#         }
    
#     def _handle_procedural_query(self, query: str, user_context: Dict) -> Dict:
#         """Handle how-to questions"""
#         # Search documentation in vector store
#         vector_results = self.rag_service.vectorstore.search(query, k=3)
#         context = [r['content'] for r in vector_results if r.get('content')]
        
#         response = self.groq_service.generate_response(query, context)
        
#         return {
#             "query": query,
#             "response": response['response'],
#             "query_type": "procedural",
#             "sources": len(vector_results),
#             "tokens_used": response.get('tokens_used', 0),
#             "success": response.get('success', False),
#             "context_sources": {"vector_store": len(vector_results)},
#             "response_time": 0.0
#         }





# ============================================
# FIXED ORCHESTRATOR
# File: apps/rag_system/services/orchestrator.py
# ============================================

from typing import Dict
from enum import Enum
from .rag_service import RAGService
from .groq_service import GroqService


class QueryType(Enum):
    """Types of queries"""
    FACTUAL = "factual"  # Simple database lookup
    ANALYTICAL = "analytical"  # Requires computation
    CONVERSATIONAL = "conversational"  # General chat
    PROCEDURAL = "procedural"  # How-to questions


class RAGOrchestrator:
    """Orchestrate RAG workflow with intelligence"""
    
    def __init__(self):
        print("Initializing RAG Orchestrator...")
        self.rag_service = RAGService()
        self.groq_service = GroqService()
        print("RAG Orchestrator ready!")
    
    def process_intelligent_query(self, query: str, user_context: Dict) -> Dict:
        """Intelligently process query based on type"""
        
        # Step 1: Classify query type
        query_type = self._classify_query(query)
        print(f"Query classified as: {query_type.value}")
        
        # Step 2: Route to appropriate handler
        if query_type == QueryType.FACTUAL:
            return self._handle_factual_query(query, user_context)
        elif query_type == QueryType.ANALYTICAL:
            return self._handle_analytical_query(query, user_context)
        elif query_type == QueryType.CONVERSATIONAL:
            return self._handle_conversational_query(query, user_context)
        else:
            return self._handle_procedural_query(query, user_context)
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query type using keywords"""
        query_lower = query.lower()
        
        # ✅ EXPANDED: Database/LMS-related keywords (HIGH PRIORITY)
        database_keywords = [
            # Counting
            'how many', 'count', 'total', 'number of',
            
            # Listing/Showing
            'show', 'list', 'display', 'get', 'find', 'search',
            'give me', 'tell me', 'what are', 'show me',
            
            # LMS Entities
            'student', 'students', 'teacher', 'teachers',
            'class', 'classes', 'subject', 'subjects',
            'fee', 'fees', 'payment', 'invoice',
            'exam', 'test', 'result', 'grade', 'marks',
            'attendance', 'absent', 'present',
            'route', 'routes', 'transport', 'bus', 'vehicle',
            'book', 'books', 'library',
            'hostel', 'room', 'allocation',
            'assignment', 'homework',
            
            # Actions
            'enrolled', 'registered', 'assigned', 'allocated',
            'pending', 'overdue', 'paid', 'unpaid',
            'active', 'inactive',
        ]
        
        # Check if query is about database/LMS data
        if any(keyword in query_lower for keyword in database_keywords):
            # If it's counting or aggregating, it's analytical
            if any(word in query_lower for word in ['how many', 'count', 'total', 'average', 'sum']):
                return QueryType.ANALYTICAL
            # Otherwise it's factual (listing/showing)
            else:
                return QueryType.FACTUAL
        
        # Check for procedural queries (how-to)
        procedural_keywords = [
            'how to', 'how do i', 'how can i', 'steps', 
            'guide', 'tutorial', 'procedure', 'process'
        ]
        if any(kw in query_lower for kw in procedural_keywords):
            return QueryType.PROCEDURAL
        
        # Default to conversational for greetings and general chat
        conversational_keywords = [
            'hello', 'hi', 'hey', 'thanks', 'thank you',
            'good morning', 'good afternoon', 'good evening',
            'what can you do', 'help me', 'who are you'
        ]
        if any(kw in query_lower for kw in conversational_keywords):
            return QueryType.CONVERSATIONAL
        
        # Default: Try factual first (search database)
        return QueryType.FACTUAL
    
    def _handle_factual_query(self, query: str, user_context: Dict) -> Dict:
        """Handle factual queries - direct database lookups"""
        result = self.rag_service.process_query(query, user_context, use_cache=True)
        result['query_type'] = 'factual'
        return result
    
    def _handle_analytical_query(self, query: str, user_context: Dict) -> Dict:
        """Handle analytical queries - require computation"""
        result = self.rag_service.process_query(query, user_context, use_cache=False)
        result['query_type'] = 'analytical'
        return result
    
    def _handle_conversational_query(self, query: str, user_context: Dict) -> Dict:
        """Handle general conversation"""
        system_prompt = f"""You are a helpful LMS assistant. 
User info: {user_context.get('username', 'User')} ({user_context.get('user_type', 'user')})
Be friendly, conversational, and helpful."""
        
        response = self.groq_service.generate_response(query, [], system_prompt)
        
        return {
            "query": query,
            "response": response['response'],
            "query_type": "conversational",
            "tokens_used": response.get('tokens_used', 0),
            "success": response.get('success', False),
            "context_sources": {},
            "response_time": 0.0
        }
    
    def _handle_procedural_query(self, query: str, user_context: Dict) -> Dict:
        """Handle how-to questions"""
        # Search documentation in vector store
        vector_results = self.rag_service.vectorstore.search(query, k=3)
        context = [r['content'] for r in vector_results if r.get('content')]
        
        response = self.groq_service.generate_response(query, context)
        
        return {
            "query": query,
            "response": response['response'],
            "query_type": "procedural",
            "sources": len(vector_results),
            "tokens_used": response.get('tokens_used', 0),
            "success": response.get('success', False),
            "context_sources": {"vector_store": len(vector_results)},
            "response_time": 0.0
        }