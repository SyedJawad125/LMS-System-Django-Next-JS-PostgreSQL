# from typing import Dict, List
# import hashlib
# import time
# from .groq_service import GroqService
# from .database_connector import DatabaseConnector
# from .vectorstore_service import VectorStoreService
# from .pdf_reader import DocumentReader


# class RAGService:
#     """Main RAG Service - Coordinates all components"""
    
#     def __init__(self):
#         print("Initializing RAG Service...")
#         self.groq_service = GroqService()
#         self.db_connector = DatabaseConnector()
#         self.vectorstore = VectorStoreService()
#         self.doc_reader = DocumentReader()
#         print("RAG Service initialized!")
    
#     def process_query(
#         self, 
#         query: str, 
#         user_context: Dict = None,
#         use_cache: bool = True
#     ) -> Dict:
#         """Process user query with RAG"""
#         start_time = time.time()
        
#         # Check cache
#         if use_cache:
#             cached = self._check_cache(query)
#             if cached:
#                 cached['response_time'] = time.time() - start_time
#                 return cached
        
#         try:
#             # Step 1: Retrieve relevant context from vector store
#             print(f"Searching vector store for: {query}")
#             vector_results = self.vectorstore.search(query, k=5)
            
#             # Step 2: Search database for relevant data
#             print("Searching database...")
#             db_results = self.db_connector.search_relevant_data(query, limit=5)
            
#             # Step 3: Check if SQL query needed
#             sql_query = None
#             sql_results = []
            
#             if self._needs_sql_query(query):
#                 print("Generating SQL query...")
#                 schema = self.db_connector.get_schema_info()
#                 sql_query = self.groq_service.generate_sql_query(query, schema)
                
#                 if sql_query:
#                     print(f"Executing SQL: {sql_query}")
#                     sql_results = self.db_connector.execute_query(sql_query)
            
#             # Step 4: Combine all context
#             context = self._build_context(vector_results, db_results, sql_results)
            
#             # Step 5: Generate response with GROQ
#             print("Generating response with GROQ...")
#             response_data = self.groq_service.generate_response(query, context, user_context)
            
#             # Calculate response time
#             response_time = time.time() - start_time
            
#             result = {
#                 "query": query,
#                 "response": response_data.get("response", ""),
#                 "context_sources": {
#                     "vector_store": len(vector_results),
#                     "database_search": len(db_results),
#                     "sql_query": sql_query,
#                     "sql_results_count": len(sql_results)
#                 },
#                 "tokens_used": response_data.get("tokens_used", 0),
#                 "response_time": response_time,
#                 "success": response_data.get("success", False),
#                 "cached": False
#             }
            
#             # Cache the result
#             if use_cache and result["success"]:
#                 self._cache_result(query, result)
            
#             return result
            
#         except Exception as e:
#             print(f"Error in RAG process: {e}")
#             import traceback
#             traceback.print_exc()
            
#             return {
#                 "query": query,
#                 "response": f"Sorry, I encountered an error: {str(e)}",
#                 "context_sources": {},
#                 "tokens_used": 0,
#                 "response_time": time.time() - start_time,
#                 "success": False,
#                 "error": str(e)
#             }
    
#     def _needs_sql_query(self, query: str) -> bool:
#         """Determine if query needs SQL execution"""
#         sql_keywords = [
#             'how many', 'count', 'total', 'list all', 'show me',
#             'find', 'search', 'get', 'who are', 'which',
#             'students', 'teachers', 'fees', 'fee', 'payment',
#             'attendance', 'results', 'marks', 'grade', 'class'
#         ]
#         query_lower = query.lower()
#         return any(keyword in query_lower for keyword in sql_keywords)
    
#     def _build_context(
#         self, 
#         vector_results: List[Dict], 
#         db_results: List[Dict],
#         sql_results: List[Dict]
#     ) -> List[str]:
#         """Build context list from all sources"""
#         context = []
        
#         # Add vector store results
#         for result in vector_results:
#             if result.get('content'):
#                 context.append(result['content'])
        
#         # Add database search results
#         for result in db_results:
#             context.append(str(result))
        
#         # Add SQL query results (most important)
#         if sql_results:
#             # Format SQL results nicely
#             formatted_results = "Database Query Results:\n"
#             for i, row in enumerate(sql_results[:10], 1):  # Limit to 10 rows
#                 formatted_results += f"\nRow {i}:\n"
#                 for key, value in row.items():
#                     formatted_results += f"  {key}: {value}\n"
#             context.insert(0, formatted_results)  # Put at beginning
        
#         return context[:10]  # Limit to top 10 contexts
    
#     def _check_cache(self, query: str) -> Dict:
#         """Check if query is cached"""
#         try:
#             from apps.rag_system.models import QueryCache
            
#             query_hash = hashlib.sha256(query.encode()).hexdigest()
            
#             cached = QueryCache.objects.get(query_hash=query_hash)
#             cached.hit_count += 1
#             cached.save()
            
#             print(f"Cache HIT for query (hits: {cached.hit_count})")
            
#             return {
#                 "query": query,
#                 "response": cached.response,
#                 "cached": True,
#                 "context_sources": cached.context,
#                 "tokens_used": 0,
#                 "success": True
#             }
#         except Exception:
#             print("Cache MISS")
#             return None
    
#     def _cache_result(self, query: str, result: Dict):
#         """Cache query result"""
#         try:
#             from apps.rag_system.models import QueryCache
            
#             query_hash = hashlib.sha256(query.encode()).hexdigest()
            
#             QueryCache.objects.update_or_create(
#                 query_hash=query_hash,
#                 defaults={
#                     'query_text': query,
#                     'response': result['response'],
#                     'context': result['context_sources']
#                 }
#             )
#             print("Query result cached")
#         except Exception as e:
#             print(f"Error caching result: {e}")
    
#     def index_database_tables(self, table_names: List[str] = None):
#         """Index database tables into vector store"""
#         if not table_names:
#             # Default important tables
#             table_names = [
#                 'students', 'teachers', 'classes', 'sections',
#                 'subjects', 'attendance', 'exam_results', 
#                 'fee_invoices', 'books'
#             ]
        
#         print(f"Indexing {len(table_names)} tables...")
        
#         for table_name in table_names:
#             try:
#                 # Get recent records
#                 query = f"SELECT * FROM {table_name} LIMIT 100"
#                 results = self.db_connector.execute_query(query)
                
#                 if results:
#                     self.vectorstore.add_database_context(table_name, results)
#                     print(f"✓ Indexed {len(results)} records from {table_name}")
#                 else:
#                     print(f"✗ No data found in {table_name}")
#             except Exception as e:
#                 print(f"✗ Error indexing {table_name}: {e}")
        
#         print("Database indexing complete!")


# ============================================
# COMPLETE FIX: RAG Service
# File: apps/rag_system/services/rag_service.py
# ============================================

from typing import Dict, List
import hashlib
import time
from .groq_service import GroqService
from .database_connector import DatabaseConnector
from .vectorstore_service import VectorStoreService
from .pdf_reader import DocumentReader


class RAGService:
    """Main RAG Service - Coordinates all components"""
    
    def __init__(self):
        print("Initializing RAG Service...")
        self.groq_service = GroqService()
        self.db_connector = DatabaseConnector()
        self.vectorstore = VectorStoreService()
        self.doc_reader = DocumentReader()
        print("RAG Service initialized!")
    
    # Update the process_query method:

    def process_query(self, query: str, user_context: Dict = None, use_cache: bool = True) -> Dict:
        """Process query with proper SQL generation and execution"""
        start_time = time.time()
        
        # Check cache
        if use_cache:
            cached = self._check_cache(query)
            if cached:
                cached['response_time'] = time.time() - start_time
                return cached
        
        try:
            # Initialize query planner
            from .query_planner import QueryPlanner
            planner = QueryPlanner(self.db_connector)
            
            # Create execution plan
            plan = planner.plan_query_execution(query)
            print(f"📋 Query Plan: {plan}")
            
            context_sources = {
                "vector_store": 0,
                "database_search": 0,
                "sql_query": None,
                "sql_results_count": 0,
                "sql_error": None,
                "plan_executed": plan["steps"],
                "tables_attempted": plan["expected_tables"]
            }
            
            context = []
            sql_results = []
            sql_query = None
            
            # STEP 1: Try SQL execution if tables are found
            if plan["needs_sql"] and plan["expected_tables"]:
                print(f"🎯 Attempting SQL execution with tables: {plan['expected_tables']}")
                
                # Get detailed table information
                table_info = planner.get_table_info_for_sql(plan["expected_tables"])
                
                if table_info:
                    print(f"📊 Got detailed info for {len(table_info)} tables")
                    
                    # Generate SQL with table info
                    sql_query = self.groq_service.generate_intelligent_sql(query, table_info)
                    context_sources["sql_query"] = sql_query
                    
                    if sql_query:
                        print(f"🚀 Executing SQL: {sql_query}")
                        
                        try:
                            sql_results = self.db_connector.execute_query(sql_query)
                            context_sources["sql_results_count"] = len(sql_results)
                            
                            # Add SQL results to context
                            if sql_results:
                                formatted_sql = "DATABASE QUERY RESULTS:\n"
                                formatted_sql += f"Query: {sql_query}\n"
                                formatted_sql += f"Found {len(sql_results)} records:\n\n"
                                
                                for i, row in enumerate(sql_results[:5], 1):
                                    formatted_sql += f"Record {i}:\n"
                                    for key, value in row.items():
                                        formatted_sql += f"  {key}: {value}\n"
                                    formatted_sql += "\n"
                                
                                if len(sql_results) > 5:
                                    formatted_sql += f"... and {len(sql_results)-5} more records\n"
                                
                                context.append(formatted_sql)
                                print(f"✅ SQL returned {len(sql_results)} results")
                            else:
                                context.append("DATABASE QUERY: No results found for the SQL query.\n")
                                print("ℹ️ SQL query returned 0 results")
                        
                        except Exception as sql_error:
                            error_msg = f"SQL Execution Error: {str(sql_error)}"
                            context_sources["sql_error"] = error_msg
                            context.append(f"DATABASE ERROR: {error_msg}\n")
                            print(f"❌ SQL execution failed: {sql_error}")
                    else:
                        print("⚠️ Failed to generate SQL query")
                else:
                    print("⚠️ Could not get table information")
            
            # STEP 2: If no SQL results, try vector store
            if context_sources["sql_results_count"] == 0 and not context_sources.get("sql_error"):
                print("🔍 Searching vector store as fallback...")
                vector_results = self.vectorstore.search(query, k=5)
                context_sources["vector_store"] = len(vector_results)
                
                if vector_results:
                    context.append("DOCUMENT CONTEXT (from uploaded files):\n")
                    for i, result in enumerate(vector_results[:3], 1):
                        if result.get('content'):
                            context.append(f"Document {i}:\n{result['content'][:500]}...\n")
                    print(f"✅ Vector store found {len(vector_results)} documents")
                else:
                    context.append("No relevant documents found in vector store.\n")
            
            # STEP 3: Generate final response
            print("🤖 Generating final response...")
            
            # Build intelligent prompt
            custom_prompt = self._build_context_aware_prompt(
                query, 
                context_sources, 
                sql_results, 
                plan
            )
            
            response_data = self.groq_service.generate_response(query, context, custom_prompt)
            
            # STEP 4: Prepare final result
            response_time = time.time() - start_time
            
            result = {
                "query": query,
                "response": response_data.get("response", "No response generated"),
                "context_sources": context_sources,
                "tokens_used": response_data.get("tokens_used", 0),
                "response_time": response_time,
                "success": response_data.get("success", False),
                "cached": False,
                "query_plan": plan,
                "query_type": plan["query_type"]
            }
            
            # Cache result
            if use_cache and result["success"]:
                self._cache_result(query, result)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in RAG process: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "query": query,
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "context_sources": {},
                "tokens_used": 0,
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }

    def _build_context_aware_prompt(self, query: str, context_sources: Dict, sql_results: List, plan: Dict) -> str:
        """Build intelligent prompt based on execution results"""
        
        prompt_parts = [
            "You are an intelligent LMS assistant analyzing query results.",
            f"User Query: '{query}'",
            "\nEXECUTION SUMMARY:"
        ]
        
        # Add SQL results info
        if context_sources["sql_query"]:
            prompt_parts.append(f"- SQL Query was generated and executed")
            prompt_parts.append(f"- SQL returned {len(sql_results)} results")
            
            if sql_results:
                prompt_parts.append("- Use the SQL results as PRIMARY source for your answer")
            else:
                prompt_parts.append("- SQL query returned 0 results (table might be empty)")
        
        # Add vector store info
        if context_sources["vector_store"] > 0:
            prompt_parts.append(f"- Vector store found {context_sources['vector_store']} relevant documents")
            if context_sources["sql_results_count"] == 0:
                prompt_parts.append("- Use document context as PRIMARY source")
        
        # Add tables attempted
        if context_sources["tables_attempted"]:
            prompt_parts.append(f"- Attempted to query tables: {', '.join(context_sources['tables_attempted'])}")
        
        # Add error info if any
        if context_sources.get("sql_error"):
            prompt_parts.append(f"- SQL Error occurred: {context_sources['sql_error']}")
            prompt_parts.append("- Acknowledge the database error in your response")
        
        # Add instructions
        prompt_parts.append("\nRESPONSE INSTRUCTIONS:")
        prompt_parts.append("1. If SQL results exist, use them as the main answer")
        prompt_parts.append("2. If no SQL results but documents exist, use document context")
        prompt_parts.append("3. Be honest about what data was found")
        prompt_parts.append("4. If conflicting info, mention the discrepancy")
        prompt_parts.append("5. Provide specific numbers when available")
        prompt_parts.append("6. If database error, explain it clearly")
        
        return "\n".join(prompt_parts)

    def _build_agentic_prompt(self, context_sources: Dict, plan: Dict) -> str:
        """Build intelligent prompt based on what was found"""
        
        prompt_parts = ["You are an intelligent LMS assistant with access to multiple data sources."]
        
        # Add what was found
        if context_sources["sql_results_count"] > 0:
            prompt_parts.append(f"Database query returned {context_sources['sql_results_count']} results.")
        else:
            prompt_parts.append("No database results found.")
        
        if context_sources["vector_store"] > 0:
            prompt_parts.append(f"Found {context_sources['vector_store']} relevant documents.")
        
        prompt_parts.append("\nINSTRUCTIONS:")
        prompt_parts.append("1. Use database results if available")
        prompt_parts.append("2. If no database results, use document context")
        prompt_parts.append("3. Be honest about what data exists")
        prompt_parts.append("4. If conflicting information, note the discrepancy")
        prompt_parts.append("5. Provide specific numbers when available")
        
        return "\n".join(prompt_parts)
        
    def _is_database_query(self, query: str) -> bool:
        """Check if query needs database access"""
        query_lower = query.lower()
        
        database_indicators = [
            # Counting
            'how many', 'count', 'total', 'number of',
            # Listing
            'show', 'list', 'display', 'get', 'find',
            'tell me', 'give me', 'what are',
            # Entities
            'student', 'teacher', 'class', 'subject',
            'fee', 'payment', 'exam', 'result',
            'attendance', 'route', 'vehicle', 'bus',
            'book', 'library', 'hostel'
        ]
        
        return any(indicator in query_lower for indicator in database_indicators)
    
    def _build_context(
        self, 
        vector_results: List[Dict], 
        db_results: List[Dict],
        sql_results: List[Dict]
    ) -> List[str]:
        """Build context list from all sources"""
        context = []
        
        # ✅ PRIORITY: SQL query results (most important)
        if sql_results:
            formatted_sql = "Database Query Results:\n"
            for i, row in enumerate(sql_results[:20], 1):  # Limit to 20 rows
                formatted_sql += f"\nRecord {i}:\n"
                for key, value in row.items():
                    formatted_sql += f"  {key}: {value}\n"
            context.insert(0, formatted_sql)  # Put at the beginning
        
        # Add database search results
        for result in db_results:
            context.append(str(result))
        
        # Add vector store results
        for result in vector_results:
            if result.get('content'):
                context.append(result['content'])
        
        return context[:15]  # Limit total contexts
    
    def _check_cache(self, query: str) -> Dict:
        """Check if query is cached"""
        try:
            from apps.rag_system.models import QueryCache
            
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            
            cached = QueryCache.objects.get(query_hash=query_hash)
            cached.hit_count += 1
            cached.save()
            
            print(f"✅ Cache HIT (hits: {cached.hit_count})")
            
            return {
                "query": query,
                "response": cached.response,
                "cached": True,
                "context_sources": cached.context,
                "tokens_used": 0,
                "success": True
            }
        except Exception:
            print("ℹ️ Cache MISS")
            return None
    
    def _cache_result(self, query: str, result: Dict):
        """Cache query result"""
        try:
            from apps.rag_system.models import QueryCache
            
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            
            QueryCache.objects.update_or_create(
                query_hash=query_hash,
                defaults={
                    'query_text': query,
                    'response': result['response'],
                    'context': result['context_sources']
                }
            )
            print("✅ Query result cached")
        except Exception as e:
            print(f"⚠️ Error caching result: {e}")
    
    def index_database_tables(self, table_names: List[str] = None):
        """Index database tables into vector store"""
        if not table_names:
            table_names = [
                'students', 'teachers', 'classes', 'sections',
                'subjects', 'attendance', 'exam_results', 
                'fee_invoices', 'books', 'routes', 'vehicles'
            ]
        
        print(f"📊 Indexing {len(table_names)} tables...")
        
        for table_name in table_names:
            try:
                query = f"SELECT * FROM {table_name} WHERE deleted = FALSE OR deleted IS NULL LIMIT 100"
                results = self.db_connector.execute_query(query)
                
                if results:
                    self.vectorstore.add_database_context(table_name, results)
                    print(f"✅ Indexed {len(results)} records from {table_name}")
                else:
                    print(f"ℹ️ No data in {table_name}")
            except Exception as e:
                print(f"⚠️ Error indexing {table_name}: {e}")
        
        print("✅ Database indexing complete!")
