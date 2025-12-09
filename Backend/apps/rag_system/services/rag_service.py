# # RAG SERVICE CODE

# from typing import Dict, List
# import time
# from .groq_service import GroqService
# from .vectorstore_service import VectorStoreService


# class VectorStoreRAGService:
#     """RAG Service that uses ONLY vector store for all queries"""
    
#     def __init__(self):
#         print("🚀 Initializing Vector-Only RAG Service...")
#         self.groq_service = GroqService()
#         self.vectorstore = VectorStoreService()
        
#         # Initialize with database knowledge
#         self._initialize_knowledge_base()
        
#         print("✅ RAG Service ready! (Vector Store Only)")
    
#     def _initialize_knowledge_base(self):
#         """Initialize vector store with comprehensive knowledge"""
#         # Mock tables list (you can replace with actual tables if needed)
#         mock_tables = [
#             "users_user", "students", "teachers_teacher", "users_role",
#             "classes", "subjects", "exams", "fee_invoices", "fee_payments",
#             "daily_attendance", "vehicles", "routes", "parents", 
#             "images_images", "users_employee"
#         ]
        
#         self.vectorstore.initialize_with_database_knowledge(mock_tables)
    
#     def process_query(self, query: str, user_context: Dict = None, use_cache: bool = True) -> Dict:
#         """Process query using ONLY vector store"""
#         start_time = time.time()
        
#         print(f"\n🔍 Processing query: '{query}'")
#         print("📚 Using vector store for response...")
        
#         try:
#             # Step 1: Search vector store
#             search_results = self.vectorstore.search(query, k=8)
            
#             # Step 2: Generate initial answer from vector store
#             vector_answer = self.vectorstore.generate_answer(query, search_results)
            
#             # Step 3: Enhance with GROQ for natural language
#             context = []
#             for result in search_results[:3]:
#                 if result.get("content"):
#                     content = result["content"]
#                     # Truncate long content
#                     if len(content) > 500:
#                         content = content[:500] + "..."
#                     context.append(content)
            
#             # Create enhanced system prompt
#             system_prompt = self._create_system_prompt(query, search_results)
            
#             # Generate final response
#             response_data = self.groq_service.generate_response(
#                 query=query,
#                 context=context,
#                 system_prompt=system_prompt
#             )
            
#             response_time = time.time() - start_time
            
#             # Prepare result
#             result = {
#                 "query": query,
#                 "response": response_data.get("response", vector_answer),
#                 "context_sources": {
#                     "vector_store_results": len(search_results),
#                     "response_method": "vector_store_only",
#                     "query_type": self._classify_query(query),
#                     "top_sources": [r.get("metadata", {}).get("type", "unknown") for r in search_results[:3]]
#                 },
#                 "tokens_used": response_data.get("tokens_used", 0),
#                 "response_time": response_time,
#                 "success": response_data.get("success", True),
#                 "cached": False
#             }
            
#             return result
            
#         except Exception as e:
#             print(f"❌ Error processing query: {e}")
            
#             return {
#                 "query": query,
#                 "response": f"I encountered an error: {str(e)[:100]}...",
#                 "context_sources": {},
#                 "tokens_used": 0,
#                 "response_time": time.time() - start_time,
#                 "success": False,
#                 "error": str(e)
#             }
    
#     def _create_system_prompt(self, query: str, search_results: List[Dict]) -> str:
#         """Create system prompt based on query and results"""
        
#         # Extract entity type from query
#         entity_type = self._extract_entity_type(query)
        
#         # Extract patterns from results
#         patterns = []
#         for result in search_results[:3]:
#             metadata = result.get("metadata", {})
#             if metadata.get("type") == "query_pattern":
#                 patterns.append(metadata.get("pattern", ""))
        
#         prompt_parts = [
#             "You are an intelligent LMS assistant. Use the provided context to answer questions.",
#             f"User Query: '{query}'",
#             "",
#             "RESPONSE GUIDELINES:"
#         ]
        
#         if entity_type:
#             prompt_parts.append(f"1. This query is about {entity_type}s")
#             prompt_parts.append(f"2. Provide specific {entity_type}-related information")
        
#         if "counting" in patterns:
#             prompt_parts.append("3. This is a counting query - provide exact numbers if available")
#             prompt_parts.append("4. If exact numbers aren't known, provide typical ranges")
        
#         if "listing" in patterns:
#             prompt_parts.append("5. This is a listing query - provide clear lists")
#             prompt_parts.append("6. Group similar items together")
        
#         prompt_parts.append("")
#         prompt_parts.append("CONTEXT INFORMATION:")
#         prompt_parts.append("The following information is from the LMS knowledge base:")
        
#         # Add context summary
#         for i, result in enumerate(search_results[:3], 1):
#             metadata = result.get("metadata", {})
#             content_preview = result.get("content", "")[:200]
#             prompt_parts.append(f"Source {i} [{metadata.get('type', 'info')}]: {content_preview}...")
        
#         prompt_parts.append("")
#         prompt_parts.append("IMPORTANT:")
#         prompt_parts.append("- Base your answer on the provided context")
#         prompt_parts.append("- Be specific and accurate")
#         prompt_parts.append("- If information is missing, say so clearly")
#         prompt_parts.append("- Use natural, helpful language")
        
#         return "\n".join(prompt_parts)
    
#     def _classify_query(self, query: str) -> str:
#         """Classify query type"""
#         query_lower = query.lower()
        
#         if any(word in query_lower for word in ["how many", "count", "total", "number of"]):
#             return "counting"
#         elif any(word in query_lower for word in ["show", "list", "display", "get all"]):
#             return "listing"
#         elif any(word in query_lower for word in ["details", "information", "tell me about", "explain"]):
#             return "details"
#         elif any(word in query_lower for word in ["with", "where", "having", "by", "for"]):
#             return "filtering"
#         else:
#             return "general"
    
#     def _extract_entity_type(self, query: str) -> str:
#         """Extract entity type from query"""
#         query_lower = query.lower()
        
#         entities = {
#             "user": ["user", "account", "profile"],
#             "student": ["student", "pupil", "learner"],
#             "teacher": ["teacher", "instructor", "faculty"],
#             "role": ["role", "position", "permission"],
#             "class": ["class", "grade", "section"],
#             "subject": ["subject", "course"],
#             "exam": ["exam", "test", "assessment"],
#             "fee": ["fee", "payment", "invoice"],
#             "attendance": ["attendance", "presence"],
#             "vehicle": ["vehicle", "bus", "transport"],
#             "route": ["route", "path"],
#             "parent": ["parent", "guardian"],
#             "book": ["book", "library", "publication"],
#             "employee": ["employee", "staff"]
#         }
        
#         for entity, keywords in entities.items():
#             for keyword in keywords:
#                 if keyword in query_lower:
#                     return entity
        
#         return "unknown"



# ============================================
# ENHANCED RAG SERVICE
# File: apps/rag_system/services/rag_service.py
# ============================================

from typing import Dict, List
import time
from .groq_service import GroqService
from .vectorstore_service import VectorStoreService
from .database_connector import DatabaseConnector


class VectorStoreRAGService:
    """Enhanced RAG Service with PostgreSQL + Vector Store"""
    
    def __init__(self):
        print("🚀 Initializing Enhanced RAG Service...")
        self.groq_service = GroqService()
        self.vectorstore = VectorStoreService()
        self.db_connector = DatabaseConnector()
        
        # Initialize vector store with database knowledge
        self._initialize_knowledge_base()
        
        print("✅ Enhanced RAG Service ready!")
    
    def _initialize_knowledge_base(self):
        """Initialize vector store with PostgreSQL database knowledge"""
        try:
            self.vectorstore.initialize_with_database_knowledge(refresh=False)
        except Exception as e:
            print(f"⚠️ Error initializing knowledge base: {e}")
    
    def process_query(self, query: str, user_context: Dict = None, use_cache: bool = True) -> Dict:
        """Process query using Vector Store + Database"""
        start_time = time.time()
        
        print(f"\n🔍 Processing query: '{query}'")
        
        try:
            # Step 1: Search vector store for relevant knowledge
            print("📚 Searching vector store...")
            search_results = self.vectorstore.search(query, k=10)
            
            # Step 2: Extract database context
            db_context = self._extract_database_context(query, search_results)
            
            # Step 3: Build enhanced context
            context = self._build_context(query, search_results, db_context)
            
            # Step 4: Create system prompt
            system_prompt = self._create_system_prompt(query, search_results, db_context)
            
            # Step 5: Generate response with GROQ
            print("🤖 Generating response with GROQ...")
            response_data = self.groq_service.generate_response(
                query=query,
                context=context,
                system_prompt=system_prompt
            )
            
            response_time = time.time() - start_time
            
            # Prepare result
            result = {
                "query": query,
                "response": response_data.get("response", "No response generated"),
                "context_sources": {
                    "vector_store_results": len(search_results),
                    "database_tables_used": db_context.get("tables_used", []),
                    "response_method": "vector_store_with_database",
                    "query_type": self._classify_query(query),
                    "top_sources": [
                        {
                            "type": r.get("metadata", {}).get("type", "unknown"),
                            "entity": r.get("metadata", {}).get("entity", "unknown"),
                            "score": round(r.get("score", 0), 3)
                        }
                        for r in search_results[:3]
                    ]
                },
                "tokens_used": response_data.get("tokens_used", 0),
                "response_time": round(response_time, 2),
                "success": response_data.get("success", True),
                "cached": False
            }
            
            print(f"✅ Query processed in {response_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "query": query,
                "response": f"I encountered an error processing your request: {str(e)[:200]}",
                "context_sources": {},
                "tokens_used": 0,
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    def _extract_database_context(self, query: str, search_results: List[Dict]) -> Dict:
        """Extract database context from search results"""
        print("🗄️ Extracting database context...")
        
        # Find relevant tables from search results
        tables_mentioned = set()
        entity_types = set()
        
        for result in search_results[:5]:
            metadata = result.get("metadata", {})
            
            # Extract table names
            if "table_name" in metadata:
                tables_mentioned.add(metadata["table_name"])
            
            if "main_table" in metadata:
                tables_mentioned.add(metadata["main_table"])
            
            # Extract entity types
            if "entity" in metadata:
                entity_types.add(metadata["entity"])
        
        # Also discover tables directly from query
        discovered_tables = self.db_connector.discover_relevant_tables(query)
        tables_mentioned.update(discovered_tables)
        
        # Get schema info for mentioned tables
        schema_info = {}
        for table in list(tables_mentioned)[:3]:  # Top 3 tables
            try:
                info = self.db_connector.get_table_schema_info(table)
                schema_info[table] = {
                    "columns": info.get("columns", [])[:10],
                    "row_count": info.get("row_count", 0),
                    "entity_type": info.get("entity_type", "unknown")
                }
            except Exception as e:
                print(f"⚠️ Error getting schema for {table}: {e}")
        
        return {
            "tables_used": list(tables_mentioned),
            "entity_types": list(entity_types),
            "schema_info": schema_info,
            "discovered_tables": discovered_tables
        }
    
    def _build_context(self, query: str, search_results: List[Dict], db_context: Dict) -> List[str]:
        """Build context list for GROQ"""
        context = []
        
        # Add top search results
        for i, result in enumerate(search_results[:5], 1):
            content = result.get("content", "")
            if content and len(content) > 50:
                # Truncate long content
                if len(content) > 800:
                    content = content[:800] + "..."
                
                metadata = result.get("metadata", {})
                context_type = metadata.get("type", "unknown")
                
                context.append(f"[Source {i} - {context_type}]\n{content}")
        
        # Add database context
        if db_context.get("schema_info"):
            db_info = ["[Database Schema Information]"]
            for table, info in db_context["schema_info"].items():
                db_info.append(f"• Table: {table}")
                db_info.append(f"  Columns: {', '.join(info['columns'][:8])}")
                db_info.append(f"  Records: {info['row_count']}")
                db_info.append(f"  Entity: {info['entity_type']}")
            
            context.append("\n".join(db_info))
        
        return context
    
    def _create_system_prompt(self, query: str, search_results: List[Dict], db_context: Dict) -> str:
        """Create enhanced system prompt"""
        entity_types = db_context.get("entity_types", [])
        tables_used = db_context.get("tables_used", [])
        
        prompt_parts = [
            "You are an intelligent LMS (Learning Management System) assistant with access to a PostgreSQL database.",
            "",
            "AVAILABLE INFORMATION:",
        ]
        
        # Add entity context
        if entity_types:
            prompt_parts.append(f"• Entities: {', '.join(entity_types)}")
        
        # Add table context
        if tables_used:
            prompt_parts.append(f"• Tables: {', '.join(tables_used)}")
        
        prompt_parts.extend([
            "",
            "RESPONSE GUIDELINES:",
            "1. Provide accurate, specific answers based on the context",
            "2. Use exact numbers when available from database",
            "3. Mention table names when relevant",
            "4. Be clear about what data is available",
            "5. If information is incomplete, say so",
            "6. Use natural, helpful language",
            "",
            f"USER QUERY: '{query}'",
            "",
            "Provide a helpful, accurate answer based on the context provided."
        ])
        
        return "\n".join(prompt_parts)
    
    def _classify_query(self, query: str) -> str:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["how many", "count", "total", "number of"]):
            return "counting"
        elif any(word in query_lower for word in ["show", "list", "display", "get all"]):
            return "listing"
        elif any(word in query_lower for word in ["details", "information", "tell me about"]):
            return "details"
        elif any(word in query_lower for word in ["with", "where", "having", "by", "for"]):
            return "filtering"
        else:
            return "general"
    
    def get_database_summary(self) -> Dict:
        """Get summary of database structure"""
        try:
            all_tables = self.db_connector.get_all_tables()
            
            # Filter user tables
            user_tables = [t for t in all_tables if not any(
                skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']
            )]
            
            # Get counts for main entities
            entity_counts = {}
            main_entities = {
                "users": "users_user",
                "students": "students",
                "teachers": "teachers",
                "classes": "classes",
                "exams": "exams",
                "fee_invoices": "fee_invoices"
            }
            
            for entity, table in main_entities.items():
                if table in user_tables:
                    try:
                        info = self.db_connector.get_table_schema_info(table)
                        entity_counts[entity] = info.get("row_count", 0)
                    except:
                        entity_counts[entity] = "N/A"
            
            return {
                "total_tables": len(all_tables),
                "user_tables": len(user_tables),
                "entity_counts": entity_counts,
                "sample_tables": user_tables[:20]
            }
        except Exception as e:
            return {"error": str(e)}