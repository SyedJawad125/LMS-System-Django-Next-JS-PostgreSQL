# # ============================================
# # COMPLETE FIX: RAG Service
# # File: apps/rag_system/services/rag_service.py
# # ============================================

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
    
#     # Update the process_query method:

#     # Update the SQL generation section in process_query:

#     def process_query(self, query: str, user_context: Dict = None, use_cache: bool = True) -> Dict:
#         """Process query with proper SQL generation and execution"""
#         start_time = time.time()
        
#         # Check cache
#         if use_cache:
#             cached = self._check_cache(query)
#             if cached:
#                 cached['response_time'] = time.time() - start_time
#                 return cached
        
#         try:
#             # Initialize query planner
#             from .query_planner import QueryPlanner
#             planner = QueryPlanner(self.db_connector)
            
#             # Create execution plan
#             plan = planner.plan_query_execution(query)
#             print(f"📋 Query Plan: {plan}")
            
#             # Select the best table for the query
#             best_table = self._select_best_table_for_query(query, plan["expected_tables"])
#             if best_table and "primary_table" in plan:
#                 plan["primary_table"] = best_table
#                 print(f"🎯 Selected best table: {best_table}")
            
#             context_sources = {
#                 "vector_store": 0,
#                 "database_search": 0,
#                 "sql_query": None,
#                 "sql_results_count": 0,
#                 "sql_error": None,
#                 "plan_executed": plan["steps"],
#                 "tables_attempted": plan["expected_tables"],
#                 "primary_table_used": plan.get("primary_table")
#             }
            
#             context = []
#             sql_results = []
#             sql_query = None
            
#             # STEP 1: Try SQL execution if tables are found
#             if plan["needs_sql"] and plan["expected_tables"]:
#                 primary_table = plan.get("primary_table")
#                 print(f"🎯 Primary table for SQL: {primary_table}")
                
#                 if primary_table:
#                     # Get detailed table information
#                     table_info = planner.get_table_info_for_sql([primary_table])
                    
#                     if table_info and primary_table in table_info:
#                         print(f"📊 Got detailed info for table: {primary_table}")
                        
#                         # Generate SQL with context awareness
#                         sql_query = self.groq_service.generate_context_aware_sql(
#                             query, 
#                             table_info, 
#                             plan
#                         )
#                         context_sources["sql_query"] = sql_query
                        
#                         if sql_query:
#                             print(f"🚀 Executing SQL: {sql_query}")
                            
#                             # Verify SQL uses correct table
#                             if primary_table.lower() not in sql_query.lower():
#                                 print(f"⚠️ SQL doesn't use primary table! Forcing correction...")
#                                 import re
#                                 # Find table name in SQL
#                                 from_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
#                                 if from_match:
#                                     wrong_table = from_match.group(1)
#                                     # Replace with correct table
#                                     sql_query = sql_query.replace(
#                                         f"FROM {wrong_table}", 
#                                         f"FROM {primary_table}"
#                                     )
#                                     print(f"🔄 Corrected SQL to use {primary_table}")
                            
#                             try:
#                                 sql_results = self.db_connector.execute_query(sql_query)
#                                 context_sources["sql_results_count"] = len(sql_results)
                                
#                                 # Add SQL results to context
#                                 if sql_results:
#                                     formatted_sql = self._format_sql_results(sql_query, sql_results)
#                                     context.append(formatted_sql)
#                                     print(f"✅ SQL returned {len(sql_results)} results")
                                    
#                                     # If count query returned 0, try alternative approach
#                                     if len(sql_results) == 1 and any('count' in key.lower() for key in sql_results[0].keys()):
#                                         count_value = list(sql_results[0].values())[0]
#                                         if count_value == 0:
#                                             print("🔄 Count is 0, trying alternative query...")
#                                             # Try SELECT * to see if table has data but different structure
#                                             alt_sql = f"SELECT * FROM {primary_table} LIMIT 5"
#                                             alt_results = self.db_connector.execute_query(alt_sql)
#                                             if alt_results:
#                                                 context.append(f"\nALTERNATIVE QUERY RESULTS (showing table structure):\n")
#                                                 for row in alt_results[:2]:
#                                                     context.append(str(row))
#                                 else:
#                                     context.append("DATABASE QUERY: No results found.\n")
#                                     print("ℹ️ SQL query returned 0 results")
                            
#                             except Exception as sql_error:
#                                 error_msg = str(sql_error)
#                                 context_sources["sql_error"] = error_msg
                                
#                                 # Try simpler query
#                                 print(f"🔄 SQL failed, trying simpler query...")
#                                 simple_sql = f"SELECT * FROM {primary_table} LIMIT 5"
#                                 try:
#                                     simple_results = self.db_connector.execute_query(simple_sql)
#                                     if simple_results:
#                                         context.append(f"SIMPLER QUERY RESULTS (showing table has data):\n")
#                                         for row in simple_results[:2]:
#                                             context.append(str(row))
#                                         context_sources["sql_results_count"] = len(simple_results)
#                                 except:
#                                     context.append(f"DATABASE ERROR: {error_msg}\n")
                                
#                                 print(f"❌ SQL execution failed: {error_msg}")
#                         else:
#                             print("⚠️ Failed to generate SQL query")
#                     else:
#                         print(f"⚠️ Could not get table information for {primary_table}")
#                 else:
#                     print("⚠️ No primary table identified")
            
#             # STEP 2: If no SQL results, try vector store
#             if context_sources["sql_results_count"] == 0:
#                 print("🔍 Searching vector store...")
#                 vector_results = self.vectorstore.search(query, k=5)
#                 context_sources["vector_store"] = len(vector_results)
                
#                 if vector_results:
#                     context.append("DOCUMENT CONTEXT (from uploaded files):\n")
#                     for i, result in enumerate(vector_results[:3], 1):
#                         if result.get('content'):
#                             # Clean and summarize document
#                             content = result['content']
#                             if len(content) > 500:
#                                 content = content[:500] + "..."
#                             context.append(f"Document {i}:\n{content}\n")
#                     print(f"✅ Vector store found {len(vector_results)} documents")
#                 else:
#                     context.append("No relevant documents found.\n")
            
#             # STEP 3: Generate final response
#             print("🤖 Generating final response...")
            
#             # Build intelligent prompt
#             custom_prompt = self._build_context_aware_prompt(
#                 query, 
#                 context_sources, 
#                 sql_results, 
#                 plan
#             )
            
#             response_data = self.groq_service.generate_response(query, context, custom_prompt)
            
#             # STEP 4: Prepare final result
#             response_time = time.time() - start_time
            
#             result = {
#                 "query": query,
#                 "response": response_data.get("response", "No response generated"),
#                 "context_sources": context_sources,
#                 "tokens_used": response_data.get("tokens_used", 0),
#                 "response_time": response_time,
#                 "success": response_data.get("success", False),
#                 "cached": False,
#                 "query_plan": plan,
#                 "query_type": plan["query_type"]
#             }
            
#             # Cache result
#             if use_cache and result["success"]:
#                 self._cache_result(query, result)
            
#             return result
            
#         except Exception as e:
#             print(f"❌ Error in RAG process: {e}")
#             import traceback
#             traceback.print_exc()
            
#             return {
#                 "query": query,
#                 "response": f"I encountered an error: {str(e)}. Please try again.",
#                 "context_sources": {},
#                 "tokens_used": 0,
#                 "response_time": time.time() - start_time,
#                 "success": False,
#                 "error": str(e)
#             }

#     def _select_best_table_for_query(self, query: str, tables: List[str]) -> str:
#         """Select the best table for a given query"""
#         if not tables:
#             return None
        
#         query_lower = query.lower()
        
#         # Score tables based on relevance
#         table_scores = {}
        
#         for table in tables:
#             table_lower = table.lower()
#             score = 0
            
#             # Exact matches get highest score
#             if 'role' in query_lower and 'role' in table_lower:
#                 score += 10
#             if 'user' in query_lower and 'user' in table_lower:
#                 score += 10
#             if 'permission' in query_lower and 'permission' in table_lower:
#                 score += 10
            
#             # Partial matches
#             if any(word in table_lower for word in ['role', 'permission', 'auth', 'group']):
#                 score += 5
            
#             # Prefer shorter table names (usually main tables)
#             if len(table) < 15:
#                 score += 2
            
#             table_scores[table] = score
        
#         # Return table with highest score
#         if table_scores:
#             best_table = max(table_scores.items(), key=lambda x: x[1])[0]
#             print(f"🏆 Best table selected: {best_table} (score: {table_scores[best_table]})")
#             return best_table
        
#         return tables[0]

#     def _format_sql_results(self, sql_query: str, results: List[Dict]) -> str:
#         """Format SQL results for context"""
#         formatted = f"DATABASE QUERY RESULTS:\n"
#         formatted += f"Query: {sql_query}\n"
#         formatted += f"Found {len(results)} record(s):\n\n"
        
#         if len(results) == 1 and len(results[0]) == 1:
#             # Simple count result
#             for key, value in results[0].items():
#                 formatted += f"Result: {value}\n"
#         elif len(results) <= 5:
#             # Small result set - show all
#             for i, row in enumerate(results, 1):
#                 formatted += f"Record {i}:\n"
#                 for key, value in row.items():
#                     formatted += f"  {key}: {value}\n"
#                 formatted += "\n"
#         else:
#             # Large result set - show sample
#             formatted += f"Sample (showing 3 of {len(results)}):\n"
#             for i, row in enumerate(results[:3], 1):
#                 formatted += f"Record {i}:\n"
#                 for key, value in row.items():
#                     formatted += f"  {key}: {value}\n"
#                 formatted += "\n"
#             formatted += f"... and {len(results)-3} more records\n"
        
#         return formatted

#     def _build_context_aware_prompt(self, query: str, context_sources: Dict, sql_results: List, plan: Dict) -> str:
#         """Build intelligent prompt based on execution results"""
        
#         prompt_parts = [
#             "You are an intelligent LMS assistant analyzing query results.",
#             f"User Query: '{query}'",
#             "\nEXECUTION SUMMARY:"
#         ]
        
#         # Add SQL results info
#         if context_sources["sql_query"]:
#             prompt_parts.append(f"- SQL Query was generated and executed")
#             prompt_parts.append(f"- SQL returned {len(sql_results)} results")
            
#             if sql_results:
#                 prompt_parts.append("- Use the SQL results as PRIMARY source for your answer")
#             else:
#                 prompt_parts.append("- SQL query returned 0 results (table might be empty)")
        
#         # Add vector store info
#         if context_sources["vector_store"] > 0:
#             prompt_parts.append(f"- Vector store found {context_sources['vector_store']} relevant documents")
#             if context_sources["sql_results_count"] == 0:
#                 prompt_parts.append("- Use document context as PRIMARY source")
        
#         # Add tables attempted
#         if context_sources["tables_attempted"]:
#             prompt_parts.append(f"- Attempted to query tables: {', '.join(context_sources['tables_attempted'])}")
        
#         # Add error info if any
#         if context_sources.get("sql_error"):
#             prompt_parts.append(f"- SQL Error occurred: {context_sources['sql_error']}")
#             prompt_parts.append("- Acknowledge the database error in your response")
        
#         # Add instructions
#         prompt_parts.append("\nRESPONSE INSTRUCTIONS:")
#         prompt_parts.append("1. If SQL results exist, use them as the main answer")
#         prompt_parts.append("2. If no SQL results but documents exist, use document context")
#         prompt_parts.append("3. Be honest about what data was found")
#         prompt_parts.append("4. If conflicting info, mention the discrepancy")
#         prompt_parts.append("5. Provide specific numbers when available")
#         prompt_parts.append("6. If database error, explain it clearly")
        
#         return "\n".join(prompt_parts)

#     def _build_agentic_prompt(self, context_sources: Dict, plan: Dict) -> str:
#         """Build intelligent prompt based on what was found"""
        
#         prompt_parts = ["You are an intelligent LMS assistant with access to multiple data sources."]
        
#         # Add what was found
#         if context_sources["sql_results_count"] > 0:
#             prompt_parts.append(f"Database query returned {context_sources['sql_results_count']} results.")
#         else:
#             prompt_parts.append("No database results found.")
        
#         if context_sources["vector_store"] > 0:
#             prompt_parts.append(f"Found {context_sources['vector_store']} relevant documents.")
        
#         prompt_parts.append("\nINSTRUCTIONS:")
#         prompt_parts.append("1. Use database results if available")
#         prompt_parts.append("2. If no database results, use document context")
#         prompt_parts.append("3. Be honest about what data exists")
#         prompt_parts.append("4. If conflicting information, note the discrepancy")
#         prompt_parts.append("5. Provide specific numbers when available")
        
#         return "\n".join(prompt_parts)
        
#     def _is_database_query(self, query: str) -> bool:
#         """Check if query needs database access"""
#         query_lower = query.lower()
        
#         database_indicators = [
#             # Counting
#             'how many', 'count', 'total', 'number of',
#             # Listing
#             'show', 'list', 'display', 'get', 'find',
#             'tell me', 'give me', 'what are',
#             # Entities
#             'student', 'teacher', 'class', 'subject',
#             'fee', 'payment', 'exam', 'result',
#             'attendance', 'route', 'vehicle', 'bus',
#             'book', 'library', 'hostel'
#         ]
        
#         return any(indicator in query_lower for indicator in database_indicators)
    
#     def _build_context(
#         self, 
#         vector_results: List[Dict], 
#         db_results: List[Dict],
#         sql_results: List[Dict]
#     ) -> List[str]:
#         """Build context list from all sources"""
#         context = []
        
#         # ✅ PRIORITY: SQL query results (most important)
#         if sql_results:
#             formatted_sql = "Database Query Results:\n"
#             for i, row in enumerate(sql_results[:20], 1):  # Limit to 20 rows
#                 formatted_sql += f"\nRecord {i}:\n"
#                 for key, value in row.items():
#                     formatted_sql += f"  {key}: {value}\n"
#             context.insert(0, formatted_sql)  # Put at the beginning
        
#         # Add database search results
#         for result in db_results:
#             context.append(str(result))
        
#         # Add vector store results
#         for result in vector_results:
#             if result.get('content'):
#                 context.append(result['content'])
        
#         return context[:15]  # Limit total contexts
    
#     def _check_cache(self, query: str) -> Dict:
#         """Check if query is cached"""
#         try:
#             from apps.rag_system.models import QueryCache
            
#             query_hash = hashlib.sha256(query.encode()).hexdigest()
            
#             cached = QueryCache.objects.get(query_hash=query_hash)
#             cached.hit_count += 1
#             cached.save()
            
#             print(f"✅ Cache HIT (hits: {cached.hit_count})")
            
#             return {
#                 "query": query,
#                 "response": cached.response,
#                 "cached": True,
#                 "context_sources": cached.context,
#                 "tokens_used": 0,
#                 "success": True
#             }
#         except Exception:
#             print("ℹ️ Cache MISS")
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
#             print("✅ Query result cached")
#         except Exception as e:
#             print(f"⚠️ Error caching result: {e}")
    
#     def index_database_tables(self, table_names: List[str] = None):
#         """Index database tables into vector store"""
#         if not table_names:
#             table_names = [
#                 'students', 'teachers', 'classes', 'sections',
#                 'subjects', 'attendance', 'exam_results', 
#                 'fee_invoices', 'books', 'routes', 'vehicles'
#             ]
        
#         print(f"📊 Indexing {len(table_names)} tables...")
        
#         for table_name in table_names:
#             try:
#                 query = f"SELECT * FROM {table_name} WHERE deleted = FALSE OR deleted IS NULL LIMIT 100"
#                 results = self.db_connector.execute_query(query)
                
#                 if results:
#                     self.vectorstore.add_database_context(table_name, results)
#                     print(f"✅ Indexed {len(results)} records from {table_name}")
#                 else:
#                     print(f"ℹ️ No data in {table_name}")
#             except Exception as e:
#                 print(f"⚠️ Error indexing {table_name}: {e}")
        
#         print("✅ Database indexing complete!")





# ============================================
# AUTO-DISCOVERY RAG Service
# File: apps/rag_system/services/rag_service.py
# ============================================

from typing import Dict, List
import hashlib
import time
from .groq_service import GroqService
from .database_connector import DatabaseConnector
from .vectorstore_service import VectorStoreService
from .pdf_reader import DocumentReader


# ============================================
# ESSENTIAL RAG SERVICE FIXES
# File: apps/rag_system/services/rag_service.py
# ============================================

class RAGService:
    """RAG Service with improved table handling"""
    
    def __init__(self):
        print("🚀 Initializing RAG Service...")
        self.groq_service = GroqService()
        self.db_connector = DatabaseConnector()
        self.vectorstore = VectorStoreService()
        
        print("🎯 RAG Service ready!")
    
    # UPDATE THIS METHOD - Most important fix
    def process_query(self, query: str, user_context: Dict = None, use_cache: bool = True) -> Dict:
        """Process query with improved table discovery"""
        start_time = time.time()
        
        # Check cache
        if use_cache:
            cached = self._check_cache(query)
            if cached:
                cached['response_time'] = time.time() - start_time
                return cached
        
        try:
            context_sources = {
                "vector_store": 0,
                "database_search": 0,
                "sql_query": None,
                "sql_results_count": 0,
                "sql_error": None,
                "discovered_table": None,
                "table_entity_type": "unknown",
                "table_has_data": False,
                "discovery_method": "enhanced"
            }
            
            context = []
            sql_results = []
            sql_query = None
            discovered_table = None
            
            # STEP 1: IMPROVED TABLE DISCOVERY
            print(f"\n🔍 Processing query: '{query}'")
            
            if self._is_database_query(query):
                # Use enhanced table discovery
                discovered_table = self.db_connector.get_best_table_for_query(query)
                
                if discovered_table:
                    print(f"✅ Table discovered: {discovered_table}")
                    context_sources["discovered_table"] = discovered_table
                    
                    # Analyze table
                    table_analysis = self.db_connector.analyze_table_content(discovered_table)
                    entity_type = table_analysis.get("entity_type", "unknown")
                    row_count = table_analysis.get("row_count", 0)
                    
                    context_sources.update({
                        "table_entity_type": entity_type,
                        "table_has_data": row_count > 0
                    })
                    
                    # STEP 2: GENERATE SQL WITH TABLE CONTEXT
                    table_context = {
                        "table_name": discovered_table,
                        "columns": table_analysis.get("columns", []),
                        "entity_type": entity_type,
                        "row_count": row_count
                    }
                    
                    sql_query = self._generate_smart_sql(query, table_context)
                    context_sources["sql_query"] = sql_query
                    
                    if sql_query:
                        print(f"🚀 Executing SQL: {sql_query}")
                        
                        # Execute query
                        try:
                            sql_results = self.db_connector.execute_query(sql_query)
                            context_sources["sql_results_count"] = len(sql_results)
                            
                            if sql_results:
                                print(f"✅ SQL returned {len(sql_results)} results")
                                # Format results for context
                                formatted = self._format_results_for_context(sql_results, entity_type, sql_query)
                                context.append(formatted)
                            else:
                                print("ℹ️ SQL returned 0 results")
                                context.append(f"⚠️ No results found in '{discovered_table}' table.")
                        
                        except Exception as sql_error:
                            error_msg = str(sql_error)
                            context_sources["sql_error"] = error_msg
                            print(f"❌ SQL error: {error_msg}")
                            context.append(f"⚠️ Database error: {error_msg}")
                    
                    else:
                        print("⚠️ Could not generate SQL")
                        context.append("⚠️ Could not generate database query.")
                
                else:
                    print("⚠️ No table discovered")
                    context.append("⚠️ Could not find relevant table in database.")
            
            # STEP 3: FALLBACK TO VECTOR STORE IF NEEDED
            if not sql_results and not context_sources.get("sql_error"):
                print("🔍 Searching vector store...")
                vector_results = self.vectorstore.search(query, k=3)
                context_sources["vector_store"] = len(vector_results)
                
                if vector_results:
                    context.append("📄 Document context:\n")
                    for i, result in enumerate(vector_results[:2], 1):
                        if result.get('content'):
                            content = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
                            context.append(f"[{i}] {content}\n")
            
            # STEP 4: GENERATE RESPONSE
            print("🤖 Generating response...")
            
            # Build intelligent prompt
            custom_prompt = self._build_intelligent_prompt(query, context_sources, sql_results)
            
            response_data = self.groq_service.generate_response(query, context, custom_prompt)
            
            # STEP 5: PREPARE RESULT
            response_time = time.time() - start_time
            
            result = {
                "query": query,
                "response": response_data.get("response", "No response generated"),
                "context_sources": context_sources,
                "tokens_used": response_data.get("tokens_used", 0),
                "response_time": response_time,
                "success": response_data.get("success", False),
                "cached": False,
                "discovery_method": context_sources["discovery_method"]
            }
            
            # Add query type
            query_lower = query.lower()
            if "how many" in query_lower or "count" in query_lower:
                result["query_type"] = "analytical_count"
            elif "show" in query_lower or "list" in query_lower:
                result["query_type"] = "factual_list"
            else:
                result["query_type"] = "factual"
            
            # Cache result
            if use_cache and result["success"]:
                self._cache_result(query, result)
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "query": query,
                "response": f"Error: {str(e)[:100]}...",
                "context_sources": {},
                "tokens_used": 0,
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    def _generate_smart_sql(self, query: str, table_context: Dict) -> str:
        """Generate SQL with better table understanding"""
        
        # Extract query type
        query_lower = query.lower()
        
        if "how many" in query_lower or "count" in query_lower:
            # Counting query
            table_name = table_context["table_name"]
            
            # Check for common counting patterns
            if "active" in query_lower:
                return f"SELECT COUNT(*) as count FROM {table_name} WHERE is_active = TRUE AND (deleted = FALSE OR deleted IS NULL)"
            elif "inactive" in query_lower:
                return f"SELECT COUNT(*) as count FROM {table_name} WHERE is_active = FALSE AND (deleted = FALSE OR deleted IS NULL)"
            else:
                return f"SELECT COUNT(*) as count FROM {table_name} WHERE (deleted = FALSE OR deleted IS NULL)"
        
        elif "show" in query_lower or "list" in query_lower or "get" in query_lower:
            # Listing query
            table_name = table_context["table_name"]
            columns = table_context.get("columns", [])
            
            # Select appropriate columns
            if columns:
                # Try to get name/identifier columns
                name_columns = [col for col in columns if any(word in col.lower() 
                               for word in ['name', 'title', 'email', 'username'])]
                
                if name_columns:
                    select_cols = ", ".join(name_columns[:3])
                else:
                    select_cols = "*"
            else:
                select_cols = "*"
            
            limit = 50  # Safe limit
            if "all" in query_lower:
                limit = 100
            
            return f"SELECT {select_cols} FROM {table_name} WHERE (deleted = FALSE OR deleted IS NULL) LIMIT {limit}"
        
        else:
            # Let GROQ handle it
            return self.groq_service.generate_intelligent_sql(query, table_context)
    
    def _format_results_for_context(self, results: List[Dict], entity_type: str, sql_query: str) -> str:
        """Format results nicely for context"""
        
        if not results:
            return "No results found."
        
        formatted = f"📊 Database Results ({entity_type}):\n"
        formatted += f"Query: {sql_query}\n"
        formatted += f"Found: {len(results)} record(s)\n\n"
        
        if len(results) == 1:
            # Single result (often a count)
            result = results[0]
            if len(result) == 1:
                key, value = list(result.items())[0]
                if 'count' in key.lower():
                    formatted += f"Count: {value} {entity_type}(s)\n"
                else:
                    for k, v in result.items():
                        formatted += f"{k}: {v}\n"
            else:
                for i, (k, v) in enumerate(result.items()):
                    if i < 5:  # Show first 5 fields
                        formatted += f"{k}: {v}\n"
        
        elif len(results) <= 5:
            # Small result set
            for i, row in enumerate(results, 1):
                formatted += f"Record {i}:\n"
                for j, (k, v) in enumerate(row.items()):
                    if j < 3:  # Show first 3 fields per record
                        formatted += f"  {k}: {v}\n"
                formatted += "\n"
        
        else:
            # Large result set - show summary
            formatted += f"Sample (first 3 of {len(results)}):\n"
            for i, row in enumerate(results[:3], 1):
                formatted += f"Record {i}:\n"
                for j, (k, v) in enumerate(row.items()):
                    if j < 2:  # Show first 2 fields
                        formatted += f"  {k}: {v}\n"
                formatted += "\n"
            formatted += f"... and {len(results)-3} more records\n"
        
        return formatted
    
    def _build_intelligent_prompt(self, query: str, context_sources: Dict, sql_results: List) -> str:
        """Build intelligent prompt based on what we found"""
        
        prompt_parts = [
            "You are an intelligent LMS assistant. Use the provided context to answer."
        ]
        
        # Add table information
        if context_sources.get("discovered_table"):
            prompt_parts.append(f"\nTable used: {context_sources['discovered_table']}")
            prompt_parts.append(f"Entity type: {context_sources.get('table_entity_type', 'unknown')}")
        
        # Add SQL results info
        if sql_results:
            prompt_parts.append(f"\nDatabase query returned {len(sql_results)} results.")
            
            if len(sql_results) == 1:
                result = sql_results[0]
                if len(result) == 1:
                    key, value = list(result.items())[0]
                    if 'count' in key.lower():
                        prompt_parts.append(f"Count value: {value}")
        
        # Add error info
        if context_sources.get("sql_error"):
            prompt_parts.append(f"\n⚠️ Database error: {context_sources['sql_error']}")
            prompt_parts.append("Acknowledge this error in your response.")
        
        # Instructions
        prompt_parts.append("\nInstructions:")
        prompt_parts.append("1. Use the database results if available")
        prompt_parts.append("2. Be specific with numbers")
        prompt_parts.append("3. Mention if data came from database or documents")
        prompt_parts.append("4. If no data found, say so clearly")
        
        return "\n".join(prompt_parts)
    
    # KEEP YOUR EXISTING METHODS BELOW (_is_database_query, _check_cache, etc.)
    # They should remain as is
    
    def _is_database_query(self, query: str) -> bool:
        """Check if query needs database access"""
        query_lower = query.lower()
        
        database_indicators = [
            # Counting
            'how many', 'count', 'total', 'number of',
            # Listing
            'show', 'list', 'display', 'get', 'find',
            'tell me', 'give me', 'what are',
            # Specific entities (from your 50+ models)
            'user', 'student', 'teacher', 'parent', 'role', 'permission',
            'academic', 'year', 'department', 'class', 'section', 'subject',
            'attendance', 'exam', 'result', 'grade',
            'fee', 'payment', 'invoice', 'discount',
            'book', 'library', 'issue',
            'route', 'vehicle', 'transport', 'bus',
            'hostel', 'room', 'allocation',
            'announcement', 'event', 'message', 'notification',
            'assignment', 'submission',
            'course', 'lesson', 'enrollment', 'quiz', 'question',
            'certificate', 'document',
            'leave', 'application', 'balance',
            'report', 'card', 'behavior',
            'setting', 'email', 'sms', 'template', 'log'
        ]
        
        return any(indicator in query_lower for indicator in database_indicators)
    
    def _format_sql_results(self, sql_query: str, results: List[Dict], entity_type: str = "unknown") -> str:
        """Format SQL results for context"""
        formatted = f"📊 DATABASE QUERY RESULTS ({entity_type}):\n"
        formatted += f"Query: {sql_query}\n"
        formatted += f"Found {len(results)} record(s)\n\n"
        
        if len(results) == 1 and len(results[0]) == 1:
            # Simple count result
            for key, value in results[0].items():
                formatted += f"Result: {value} {entity_type}s\n"
        elif len(results) <= 5:
            # Small result set - show all
            for i, row in enumerate(results, 1):
                formatted += f"Record {i}:\n"
                for key, value in row.items():
                    formatted += f"  {key}: {value}\n"
                formatted += "\n"
        else:
            # Large result set - show sample
            formatted += f"Sample (showing 3 of {len(results)}):\n"
            for i, row in enumerate(results[:3], 1):
                formatted += f"Record {i}:\n"
                for key, value in row.items():
                    formatted += f"  {key}: {value}\n"
                formatted += "\n"
            formatted += f"... and {len(results)-3} more records\n"
        
        return formatted
    
    def _build_auto_discovery_prompt(self, query: str, context_sources: Dict, sql_results: List, discovered_table: str) -> str:
        """Build intelligent prompt based on auto-discovery results"""
        
        prompt_parts = [
            "You are an intelligent LMS assistant that auto-discovers data from PostgreSQL.",
            f"User Query: '{query}'",
            "\nEXECUTION SUMMARY:"
        ]
        
        # Add discovery info
        if discovered_table:
            prompt_parts.append(f"- Auto-discovered table: '{discovered_table}'")
            prompt_parts.append(f"- Table type: {context_sources.get('table_entity_type', 'unknown')}")
            prompt_parts.append(f"- Table has data: {'Yes' if context_sources.get('table_has_data') else 'No'}")
        
        # Add SQL results info
        if context_sources["sql_query"]:
            prompt_parts.append(f"- SQL Query executed successfully")
            prompt_parts.append(f"- SQL returned {len(sql_results)} results")
            
            if sql_results:
                prompt_parts.append("- Use the SQL results as PRIMARY source for your answer")
                if len(sql_results) == 1:
                    first_result = sql_results[0]
                    if len(first_result) == 1:
                        count_value = list(first_result.values())[0]
                        prompt_parts.append(f"- Count value from database: {count_value}")
            else:
                prompt_parts.append("- SQL query returned 0 results (table might be empty)")
        
        # Add vector store info
        if context_sources["vector_store"] > 0:
            prompt_parts.append(f"- Found {context_sources['vector_store']} relevant documents in vector store")
            if context_sources["sql_results_count"] == 0:
                prompt_parts.append("- Using document context as fallback source")
        
        # Add error info if any
        if context_sources.get("sql_error"):
            prompt_parts.append(f"- Database Error: {context_sources['sql_error']}")
            prompt_parts.append("- Acknowledge this error in your response")
        
        # Add instructions
        prompt_parts.append("\nRESPONSE INSTRUCTIONS:")
        prompt_parts.append("1. If SQL results exist, use them as the main answer")
        prompt_parts.append("2. If SQL returned 0 results, explain what was found")
        prompt_parts.append("3. If using document context, mention it's from documents")
        prompt_parts.append("4. Be honest about data availability")
        prompt_parts.append("5. Provide specific numbers when available")
        prompt_parts.append("6. If error occurred, explain it clearly")
        prompt_parts.append("7. Mention if data was auto-discovered from PostgreSQL")
        
        return "\n".join(prompt_parts)
    
    def _build_context(
        self, 
        vector_results: List[Dict], 
        db_results: List[Dict],
        sql_results: List[Dict]
    ) -> List[str]:
        """Build context list from all sources"""
        context = []
        
        # Priority: SQL query results
        if sql_results:
            formatted_sql = "Database Query Results:\n"
            for i, row in enumerate(sql_results[:20], 1):
                formatted_sql += f"\nRecord {i}:\n"
                for key, value in row.items():
                    formatted_sql += f"  {key}: {value}\n"
            context.insert(0, formatted_sql)
        
        # Database search results
        for result in db_results:
            context.append(str(result))
        
        # Vector store results
        for result in vector_results:
            if result.get('content'):
                context.append(result['content'])
        
        return context[:15]
    
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
            # Auto-discover main tables
            all_tables = list(self.schema_info.keys())
            table_names = [t for t in all_tables if self._is_main_table(t)][:15]
        
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
    
    def _is_main_table(self, table_name: str) -> bool:
        """Check if table is a main entity table"""
        table_lower = table_name.lower()
        
        # Exclude junction tables
        exclude_patterns = [
            'mapping', 'junction', 'relation', 'link', 'token',
            'permission', 'group', 'history', 'log'
        ]
        
        for pattern in exclude_patterns:
            if pattern in table_lower:
                return False
        
        return True
    
    # Diagnostic method
    def diagnose_query(self, query: str):
        """Diagnose how the system handles a query"""
        print(f"\n🔍 DIAGNOSIS for: '{query}'")
        print("=" * 60)
        
        # Check if it's a database query
        is_db_query = self._is_database_query(query)
        print(f"Is database query: {is_db_query}")
        
        if is_db_query:
            # Discover best table
            best_table = self.db_connector.get_best_table_for_query(query)
            print(f"Best table discovered: {best_table}")
            
            if best_table:
                # Analyze table
                analysis = self.db_connector.analyze_table_content(best_table)
                print(f"Table analysis: {analysis}")
                
                # Generate SQL
                table_context = {
                    "table_name": best_table,
                    "columns": analysis.get("columns", []),
                    "entity_type": analysis.get("entity_type", "unknown")
                }
                
                sql = self.groq_service.generate_intelligent_sql(query, table_context)
                print(f"Generated SQL: {sql}")
        
        print("=" * 60)


# Quick test function
if __name__ == "__main__":
    print("🧪 Testing Auto-Discovery RAG Service")
    print("=" * 60)
    
    rag = RAGService()
    
    test_queries = [
        "how many users are there",
        "please tell me how many roles",
        "show me all students",
        "count teachers",
        "list all classes"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing: '{query}'")
        result = rag.process_query(query, use_cache=False)
        
        if result["success"]:
            print(f"✅ Success: {result['response'][:100]}...")
            print(f"📊 Table used: {result['context_sources'].get('discovered_table')}")
            print(f"📈 Results: {result['context_sources'].get('sql_results_count', 0)}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")



    # ADD THIS METHOD to RAGService class:

    def get_table_for_entity(self, entity_type: str) -> str:
        """Get the actual table name for an entity type"""
        # Mapping of common entities to actual table names
        entity_to_table = {
            'user': 'users_user',
            'student': 'students_student', 
            'teacher': 'teachers_teacher',
            'parent': 'parents',
            'role': 'users_role',
            'permission': 'users_permission',
            'class': 'classes',
            'section': 'sections',
            'subject': 'subjects',
            'course': 'courses',
            'exam': 'exams',
            'fee': 'fee_invoices',
            'payment': 'fee_payments',
            'attendance': 'daily_attendance',
            'book': 'images_images',
            'vehicle': 'vehicles',
            'route': 'routes',
            'hostel': 'hostel_rooms',  # Check if exists
            'employee': 'users_employee'
        }
        
        return entity_to_table.get(entity_type.lower())

    # UPDATE the _is_database_query method to be more specific:
    def _is_database_query(self, query: str) -> bool:
        """Check if query needs database access - IMPROVED"""
        query_lower = query.lower()
        
        # More specific patterns
        count_patterns = ['how many', 'count of', 'total number of', 'number of']
        list_patterns = ['show me', 'list all', 'display all', 'get all', 'find all']
        
        # Check for specific entity mentions
        entities = [
            'user', 'student', 'teacher', 'parent', 'role',
            'class', 'section', 'subject', 'course',
            'exam', 'fee', 'payment', 'attendance',
            'book', 'vehicle', 'route', 'employee'
        ]
        
        # If it's a counting or listing query about entities
        if any(pattern in query_lower for pattern in count_patterns + list_patterns):
            return True
        
        # If it mentions specific entities
        for entity in entities:
            if entity in query_lower:
                return True
        
        return False