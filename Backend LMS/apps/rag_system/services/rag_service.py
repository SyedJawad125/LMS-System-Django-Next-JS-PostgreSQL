# # ============================================
# # FIXED RAG SERVICE WITH DEBUGGING
# # File: apps/rag_system/services/rag_service_fixed.py
# # ============================================

# from typing import Dict, List, Optional
# import time
# import hashlib
# from collections import defaultdict
# from .groq_service import GroqService
# from .vectorstore_service import VectorStoreService
# from .database_connector import DatabaseConnector
# from .query_executor import QueryExecutor


# class VectorStoreRAGService:
#     """Fixed RAG Service with debugging"""
    
#     def __init__(self):
#         print("🚀 Initializing Fixed RAG Service v3.1...")
#         self.groq_service = GroqService()
#         self.vectorstore = VectorStoreService()
#         self.db_connector = DatabaseConnector()
#         self.query_executor = QueryExecutor()
        
#         self.query_cache = {}
#         self._initialize_knowledge_base()
        
#         print("✅ Fixed RAG Service v3.1 ready!")
    
#     def _initialize_knowledge_base(self):
#         """Initialize vector store with database knowledge"""
#         try:
#             self.vectorstore.initialize_with_database_knowledge(refresh=False)
#         except Exception as e:
#             print(f"⚠️ Error initializing knowledge base: {e}")
    
#     def process_query(
#         self, 
#         query: str, 
#         user_context: Dict = None, 
#         use_cache: bool = True,
#         use_reranking: bool = True
#     ) -> Dict:
#         """Process query with FIXED database execution"""
#         start_time = time.time()
        
#         print(f"\n{'='*60}")
#         print(f"🔍 Processing Query: '{query}'")
#         print(f"{'='*60}")
        
#         try:
#             # Step 1: Cache check
#             if use_cache:
#                 cached = self._check_cache(query)
#                 if cached:
#                     print("✅ Cache hit!")
#                     cached['cached'] = True
#                     cached['response_time'] = time.time() - start_time
#                     return cached
            
#             # Step 2: Query rewriting
#             print("\n📝 Step 1: Query Rewriting")
#             query_variations = self._rewrite_query(query)
#             print(f"   Generated {len(query_variations)} variations:")
#             for i, var in enumerate(query_variations, 1):
#                 print(f"   {i}. {var}")
            
#             # Step 3: Vector search
#             print("\n🔍 Step 2: Vector Search")
#             search_results = self._multi_query_search(query_variations, k=15)
#             print(f"   Retrieved {len(search_results)} documents")
            
#             # Debug: Show top results
#             if search_results:
#                 print("   Top 3 results:")
#                 for i, r in enumerate(search_results[:3], 1):
#                     metadata = r.get('metadata', {})
#                     print(f"     {i}. Type: {metadata.get('type')}, Entity: {metadata.get('entity')}, Score: {r.get('score', 0):.3f}")
            
#             # Step 4: Reranking
#             if use_reranking and len(search_results) > 0:
#                 print("\n🎯 Step 3: Reranking")
#                 search_results = self._rerank_results(query, search_results)
#                 print(f"   Top result score: {search_results[0].get('rerank_score', 0):.3f}")
            
#             # Step 5: Extract database context
#             print("\n🗄️ Step 4: Database Context Extraction")
#             db_context = self._extract_database_context(query, search_results)
            
#             tables_used = db_context.get("tables_used", [])
#             schema_info = db_context.get("schema_info", {})
            
#             print(f"   Tables used: {tables_used}")
#             print(f"   Schema info available for: {list(schema_info.keys())}")
            
#             # Debug schema info
#             for table in tables_used[:2]:
#                 if table in schema_info:
#                     info = schema_info[table]
#                     print(f"   {table}:")
#                     print(f"     - Columns: {info.get('columns', [])[:5]}...")
#                     print(f"     - Row count: {info.get('row_count', 0)}")
#                     print(f"     - Entity: {info.get('entity_type', 'unknown')}")
            
#             # ========================================
#             # FIXED STEP 5.5: EXECUTE DATABASE QUERY
#             # ========================================
#             print("\n💾 Step 5: Execute Database Query")
#             db_query_results = None
#             sql_executed = None
#             query_execution_success = False
#             execution_error = None
            
#             # Check preconditions
#             print(f"   Checking preconditions...")
#             print(f"   - tables_used: {bool(tables_used)}")
#             print(f"   - schema_info: {bool(schema_info)}")
            
#             if not tables_used:
#                 print(f"   ⚠️ No tables discovered from query!")
#                 execution_error = "No tables discovered"
#             elif not schema_info:
#                 print(f"   ⚠️ No schema info available!")
#                 execution_error = "No schema info"
#             else:
#                 # Get main table
#                 main_table = tables_used[0]
#                 print(f"   Main table: {main_table}")
                
#                 if main_table not in schema_info:
#                     print(f"   ⚠️ Main table '{main_table}' not in schema_info!")
#                     print(f"   Available in schema_info: {list(schema_info.keys())}")
#                     execution_error = f"Table {main_table} not in schema_info"
#                 else:
#                     # Build table context
#                     table_info = schema_info[main_table]
#                     table_context = {
#                         "table_name": main_table,
#                         "columns": table_info.get("columns", []),
#                         "entity_type": table_info.get("entity_type", "unknown"),
#                         "row_count": table_info.get("row_count", 0)
#                     }
                    
#                     print(f"   Table context built:")
#                     print(f"     - table_name: {table_context['table_name']}")
#                     print(f"     - columns count: {len(table_context['columns'])}")
#                     print(f"     - columns sample: {table_context['columns'][:5]}")
#                     print(f"     - entity_type: {table_context['entity_type']}")
                    
#                     # Execute query
#                     print(f"   Executing query...")
#                     query_result = self.query_executor.execute_user_query(
#                         query, 
#                         table_context
#                     )
                    
#                     print(f"   Query result:")
#                     print(f"     - success: {query_result['success']}")
#                     print(f"     - sql: {query_result['sql']}")
#                     print(f"     - row_count: {query_result['row_count']}")
#                     print(f"     - error: {query_result.get('error')}")
                    
#                     if query_result["success"]:
#                         db_query_results = query_result["results"]
#                         sql_executed = query_result["sql"]
#                         query_execution_success = True
                        
#                         print(f"   ✅ Success! Retrieved {len(db_query_results)} records")
                        
#                         # Show sample
#                         if db_query_results:
#                             print(f"   Sample result: {db_query_results[0]}")
#                     else:
#                         print(f"   ❌ Query failed: {query_result['error']}")
#                         execution_error = query_result['error']
            
#             if not query_execution_success:
#                 print(f"   ⚠️ Continuing without database results")
#                 print(f"   Reason: {execution_error}")
            
#             # Step 6: Build context
#             print("\n📚 Step 6: Context Building")
#             contexts = self._build_enhanced_context_with_data(
#                 query, 
#                 search_results, 
#                 db_context,
#                 db_query_results
#             )
#             print(f"   Built {len(contexts)} context chunks")
            
#             # Debug: Show what's in contexts
#             if db_query_results:
#                 print(f"   ✅ Database results included in context")
#             else:
#                 print(f"   ⚠️ No database results in context")
            
#             # Step 7: Context window management
#             print("\n✂️ Step 7: Context Window Management")
#             managed_contexts = self._manage_context_window(contexts, max_tokens=6000)
#             print(f"   Using {len(managed_contexts)} context chunks")
            
#             # Step 8: System prompt
#             print("\n🤖 Step 8: System Prompt Creation")
#             system_prompt = self._create_enhanced_system_prompt(
#                 query, 
#                 search_results, 
#                 db_context,
#                 has_database_results=(db_query_results is not None)
#             )
            
#             if db_query_results:
#                 print(f"   ✅ System prompt emphasizes using real data")
#             else:
#                 print(f"   ⚠️ System prompt does not have real data emphasis")
            
#             # Step 9: Generate response
#             print("\n💬 Step 9: Response Generation")
#             response_data = self.groq_service.generate_response(
#                 query=query,
#                 context=managed_contexts,
#                 system_prompt=system_prompt
#             )
            
#             response_time = time.time() - start_time
            
#             # Step 10: Quality evaluation
#             print("\n📊 Step 10: Quality Evaluation")
#             quality_score = self._evaluate_response_quality(
#                 query,
#                 response_data.get("response", ""),
#                 search_results,
#                 db_query_results
#             )
#             print(f"   Quality Score: {quality_score:.2f}/5.0")
            
#             # Prepare result
#             result = {
#                 "query": query,
#                 "response": response_data.get("response", "No response generated"),
#                 "context_sources": {
#                     "vector_store_results": len(search_results),
#                     "database_tables_used": tables_used,
#                     "sql_executed": sql_executed,
#                     "database_results_count": len(db_query_results) if db_query_results else 0,
#                     "query_execution_success": query_execution_success,
#                     "execution_error": execution_error,  # NEW: Include error
#                     "response_method": "fixed_rag_v3.1",
#                     "query_type": self._classify_query(query),
#                     "reranked": use_reranking,
#                     "query_variations": len(query_variations),
#                     "quality_score": quality_score,
#                     "top_sources": [
#                         {
#                             "type": r.get("metadata", {}).get("type", "unknown"),
#                             "entity": r.get("metadata", {}).get("entity", "unknown"),
#                             "score": round(r.get("score", 0), 3),
#                             "rerank_score": round(r.get("rerank_score", 0), 3) if "rerank_score" in r else None
#                         }
#                         for r in search_results[:3]
#                     ]
#                 },
#                 "database_results": db_query_results[:10] if db_query_results else [],
#                 "tokens_used": response_data.get("tokens_used", 0),
#                 "response_time": round(response_time, 2),
#                 "success": response_data.get("success", True),
#                 "cached": False
#             }
            
#             # Cache result
#             if use_cache and result['success']:
#                 self._cache_result(query, result)
            
#             print(f"\n{'='*60}")
#             print(f"✅ Query processed in {response_time:.2f}s")
#             print(f"   SQL executed: {sql_executed is not None}")
#             print(f"   Results count: {len(db_query_results) if db_query_results else 0}")
#             print(f"{'='*60}\n")
            
#             return result
            
#         except Exception as e:
#             print(f"\n❌ Error processing query: {e}")
#             import traceback
#             traceback.print_exc()
            
#             return self._fallback_response(query, str(e), time.time() - start_time)
    
#     # ========================================
#     # All other methods remain the same
#     # ========================================
    
#     def _build_enhanced_context_with_data(
#         self,
#         query: str,
#         search_results: List[Dict],
#         db_context: Dict,
#         db_query_results: Optional[List[Dict]] = None
#     ) -> List[str]:
#         """Build context including actual database results"""
#         contexts = []
        
#         # Add database results FIRST if available
#         if db_query_results and len(db_query_results) > 0:
#             print(f"   📊 Adding {len(db_query_results)} database results to context")
            
#             results_context = self.query_executor.format_results_for_llm(
#                 db_query_results,
#                 query
#             )
            
#             full_results_context = f"""[🔴 ACTUAL DATABASE QUERY RESULTS - USE THIS DATA 🔴]

# {results_context}

# [END OF DATABASE RESULTS]
# """
            
#             contexts.insert(0, full_results_context)
#         else:
#             print(f"   ⚠️ No database results to add to context")
        
#         # Add vector search results
#         for i, result in enumerate(search_results[:5], 1):
#             content = result.get("content", "")
#             if not content or len(content) < 50:
#                 continue
            
#             if len(content) > 1000:
#                 content = content[:1000] + "..."
            
#             metadata = result.get("metadata", {})
#             score = result.get("rerank_score", result.get("score", 0))
            
#             context_str = f"""[Source {i} - Relevance: {score:.3f}]
# Type: {metadata.get('type', 'unknown')}
# Entity: {metadata.get('entity', 'N/A')}
# Table: {metadata.get('table_name', 'N/A')}

# Content:
# {content}
# """
#             contexts.append(context_str)
        
#         # Add schema info
#         if db_context.get("schema_info"):
#             db_info = ["[Database Schema Information]"]
            
#             for table, info in list(db_context["schema_info"].items())[:2]:
#                 db_info.append(f"\nTable: {table}")
#                 db_info.append(f"Columns: {', '.join(info.get('columns', [])[:8])}")
#                 db_info.append(f"Records: {info.get('row_count', 0)}")
#                 db_info.append(f"Entity: {info.get('entity_type', 'unknown')}")
            
#             contexts.append("\n".join(db_info))
        
#         return contexts
    
#     def _create_enhanced_system_prompt(
#         self,
#         query: str,
#         search_results: List[Dict],
#         db_context: Dict,
#         has_database_results: bool = False
#     ) -> str:
#         """Create system prompt"""
#         entity_types = db_context.get("entity_types", [])
#         tables_used = db_context.get("tables_used", [])
        
#         prompt_parts = [
#             "You are an advanced LMS (Learning Management System) AI assistant.",
#             "",
#         ]
        
#         if has_database_results:
#             prompt_parts.extend([
#                 "🔴 CRITICAL INSTRUCTIONS - READ CAREFULLY:",
#                 "",
#                 "⚠️ **YOU HAVE ACTUAL DATABASE RESULTS IN YOUR CONTEXT**",
#                 "⚠️ **The section marked 'ACTUAL DATABASE QUERY RESULTS' contains REAL DATA**",
#                 "⚠️ **USE THIS DATA to answer the question**",
#                 "⚠️ **DO NOT say 'not available' or 'I would need access'**",
#                 "⚠️ **Give CONCRETE answers based on the results provided**",
#                 "",
#                 "✅ DO:",
#                 "- Answer directly from the database results",
#                 "- List specific values from the data",
#                 "- Be concrete and specific",
#                 "",
#                 "❌ DO NOT:",
#                 "- Say 'not available in provided database results'",
#                 "- Say 'I would need access to'",
#                 "- Say 'based on example data'",
#                 "- Be speculative or vague",
#                 "",
#             ])
        
#         prompt_parts.extend([
#             "AVAILABLE INFORMATION:",
#             "1. Real-time database query results (if present)",
#             "2. Database schema and metadata",
#             "3. Semantic search results",
#         ])
        
#         if entity_types:
#             prompt_parts.append(f"- Relevant Entities: {', '.join(entity_types)}")
        
#         if tables_used:
#             prompt_parts.append(f"- Database Tables: {', '.join(tables_used[:3])}")
        
#         prompt_parts.extend([
#             "",
#             f"USER QUERY: '{query}'",
#             "",
#             "Provide a direct, data-driven answer."
#         ])
        
#         return "\n".join(prompt_parts)
    
#     def _evaluate_response_quality(
#         self, 
#         query: str, 
#         response: str,
#         search_results: List[Dict],
#         db_query_results: Optional[List[Dict]] = None
#     ) -> float:
#         """Evaluate response quality"""
#         score = 3.0
        
#         if search_results:
#             avg_score = sum(r.get('score', 0) for r in search_results[:3]) / min(3, len(search_results))
#             if avg_score > 0.7:
#                 score += 1.0
#             elif avg_score > 0.5:
#                 score += 0.5
        
#         if db_query_results:
#             score += 0.5
#             if any(word in response.lower() for word in ['there are', 'found', 'records', 'following']):
#                 score += 0.3
        
#         response_len = len(response.split())
#         if 20 < response_len < 200:
#             score += 0.3
#         elif response_len < 10:
#             score -= 0.5
        
#         if any(char.isdigit() for char in response):
#             score += 0.2
        
#         speculation_markers = [
#             'not available in the provided', 'would need access',
#             'may not reflect', 'could be used'
#         ]
#         if any(marker in response.lower() for marker in speculation_markers):
#             score -= 1.0  # Heavy penalty
        
#         return min(5.0, max(1.0, score))
    
#     # Copy all other helper methods from the previous version
#     # (_rewrite_query, _multi_query_search, _reciprocal_rank_fusion, 
#     #  _rerank_results, _manage_context_window, _extract_database_context,
#     #  _classify_query, _check_cache, _cache_result, _fallback_response,
#     #  get_database_summary)
    
#     def _rewrite_query(self, query: str) -> List[str]:
#         """Rewrite query"""
#         variations = [query]
#         if len(query.split()) < 3:
#             return variations
#         try:
#             system_prompt = """Generate 3 alternatives:
# 1. Technical
# 2. Conversational  
# 3. Keywords
# Output only 3 rewrites, one per line."""
#             messages = [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Rewrite: {query}"}
#             ]
#             response = self.groq_service.client.chat.completions.create(
#                 model=self.groq_service.model,
#                 messages=messages,
#                 temperature=0.3,
#                 max_tokens=150
#             )
#             rewrites = response.choices[0].message.content.strip().split('\n')
#             for rewrite in rewrites[:3]:
#                 cleaned = rewrite.strip().lstrip('123456789.').strip()
#                 if cleaned and len(cleaned) > 5:
#                     variations.append(cleaned)
#         except Exception as e:
#             print(f"⚠️ Query rewriting failed: {e}")
#         return variations
    
#     def _multi_query_search(self, queries: List[str], k: int = 15) -> List[Dict]:
#         """Multi-query search"""
#         all_results = []
#         seen_content = set()
#         for i, query_var in enumerate(queries):
#             try:
#                 results = self.vectorstore.search(query_var, k=k)
#                 for result in results:
#                     content_hash = hashlib.md5(result.get('content', '')[:100].encode()).hexdigest()
#                     if content_hash not in seen_content:
#                         seen_content.add(content_hash)
#                         result['query_variation'] = i
#                         result['query_text'] = query_var
#                         all_results.append(result)
#             except Exception as e:
#                 print(f"⚠️ Search failed for '{query_var}': {e}")
#         all_results = self._reciprocal_rank_fusion(all_results)
#         all_results.sort(key=lambda x: x.get('rrf_score', 0), reverse=True)
#         return all_results[:k]
    
#     def _reciprocal_rank_fusion(self, results: List[Dict], k: int = 60) -> List[Dict]:
#         """RRF"""
#         content_scores = defaultdict(lambda: {'result': None, 'rrf_score': 0})
#         for rank, result in enumerate(results, 1):
#             content_hash = hashlib.md5(result.get('content', '')[:100].encode()).hexdigest()
#             rrf_score = 1.0 / (k + rank)
#             content_scores[content_hash]['rrf_score'] += rrf_score
#             if content_scores[content_hash]['result'] is None:
#                 content_scores[content_hash]['result'] = result
#         enhanced_results = []
#         for content_hash, data in content_scores.items():
#             result = data['result']
#             result['rrf_score'] = data['rrf_score']
#             enhanced_results.append(result)
#         return enhanced_results
    
#     def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
#         """Rerank"""
#         if not results:
#             return results
#         try:
#             for result in results:
#                 score = 0.0
#                 score += result.get('score', 0) * 0.4
#                 score += result.get('rrf_score', 0) * 0.3
#                 content_len = len(result.get('content', ''))
#                 if 200 < content_len < 2000:
#                     score += 0.1
#                 metadata = result.get('metadata', {})
#                 if metadata.get('priority') == 'high':
#                     score += 0.1
#                 if metadata.get('type') == 'entity_knowledge':
#                     score += 0.1
#                 result['rerank_score'] = score
#             results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
#         except Exception as e:
#             print(f"⚠️ Reranking failed: {e}")
#         return results
    
#     def _manage_context_window(self, contexts: List[str], max_tokens: int = 6000) -> List[str]:
#         """Manage context window"""
#         selected = []
#         total_chars = 0
#         max_chars = max_tokens * 4
#         for context in contexts:
#             context_chars = len(context)
#             if total_chars + context_chars < max_chars:
#                 selected.append(context)
#                 total_chars += context_chars
#             else:
#                 remaining = max_chars - total_chars
#                 if remaining > 500:
#                     selected.append(context[:remaining] + "...")
#                 break
#         return selected
    
#     def _extract_database_context(self, query: str, search_results: List[Dict]) -> Dict:
#         """Extract database context"""
#         tables_mentioned = set()
#         entity_types = set()
#         for result in search_results[:5]:
#             metadata = result.get("metadata", {})
#             if "table_name" in metadata:
#                 tables_mentioned.add(metadata["table_name"])
#             if "main_table" in metadata:
#                 tables_mentioned.add(metadata["main_table"])
#             if "entity" in metadata:
#                 entity_types.add(metadata["entity"])
#         discovered_tables = self.db_connector.discover_relevant_tables(query)
#         tables_mentioned.update(discovered_tables)
#         schema_info = {}
#         for table in list(tables_mentioned)[:3]:
#             try:
#                 info = self.db_connector.get_table_schema_info(table)
#                 schema_info[table] = {
#                     "columns": info.get("columns", [])[:10],
#                     "row_count": info.get("row_count", 0),
#                     "entity_type": info.get("entity_type", "unknown")
#                 }
#             except Exception as e:
#                 print(f"⚠️ Error getting schema for {table}: {e}")
#         return {
#             "tables_used": list(tables_mentioned),
#             "entity_types": list(entity_types),
#             "schema_info": schema_info,
#             "discovered_tables": discovered_tables
#         }
    
#     def _classify_query(self, query: str) -> str:
#         """Classify query"""
#         query_lower = query.lower()
#         if any(word in query_lower for word in ["how many", "count", "total", "number of"]):
#             return "counting"
#         elif any(word in query_lower for word in ["show", "list", "display", "get all"]):
#             return "listing"
#         elif any(word in query_lower for word in ["details", "information", "tell me about"]):
#             return "details"
#         elif any(word in query_lower for word in ["with", "where", "having", "by", "for"]):
#             return "filtering"
#         else:
#             return "general"
    
#     def _check_cache(self, query: str) -> Optional[Dict]:
#         """Check cache"""
#         query_hash = hashlib.md5(query.encode()).hexdigest()
#         return self.query_cache.get(query_hash)
    
#     def _cache_result(self, query: str, result: Dict):
#         """Cache result"""
#         query_hash = hashlib.md5(query.encode()).hexdigest()
#         self.query_cache[query_hash] = result
#         if len(self.query_cache) > 1000:
#             to_remove = list(self.query_cache.keys())[:100]
#             for key in to_remove:
#                 del self.query_cache[key]
    
#     def _fallback_response(self, query: str, error: str, elapsed_time: float) -> Dict:
#         """Fallback"""
#         return {
#             "query": query,
#             "response": f"I apologize, but I encountered an error processing your query.",
#             "context_sources": {"response_method": "fallback", "error": error[:200]},
#             "tokens_used": 0,
#             "response_time": round(elapsed_time, 2),
#             "success": False,
#             "cached": False
#         }
    
#     def get_database_summary(self) -> Dict:
#         """Database summary"""
#         try:
#             all_tables = self.db_connector.get_all_tables()
#             user_tables = [t for t in all_tables if not any(
#                 skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']
#             )]
#             entity_counts = {}
#             main_entities = {
#                 "users": "users_user",
#                 "students": "students",
#                 "teachers": "teachers",
#                 "classes": "classes",
#                 "exams": "exams",
#                 "fee_invoices": "fee_invoices"
#             }
#             for entity, table in main_entities.items():
#                 if table in user_tables:
#                     try:
#                         info = self.db_connector.get_table_schema_info(table)
#                         entity_counts[entity] = info.get("row_count", 0)
#                     except:
#                         entity_counts[entity] = "N/A"
#             return {
#                 "total_tables": len(all_tables),
#                 "user_tables": len(user_tables),
#                 "entity_counts": entity_counts,
#                 "sample_tables": user_tables[:20]
#             }
#         except Exception as e:
#             return {"error": str(e)}





# ============================================
# COMPLETE UPDATED RAG SERVICE
# File: apps/rag_system/services/rag_service.py
# ============================================

"""
This is the COMPLETE fixed RAG service.
Copy this to apps/rag_system/services/rag_service.py

Key improvements:
1. Integrates API data (roles/permissions)
2. Uses enhanced system prompts
3. Better context building
4. Improved response quality
"""

from typing import Dict, List, Optional
import time
import hashlib
from collections import defaultdict
from .groq_service import GroqService
from .vectorstore_service import VectorStoreService
from .database_connector import DatabaseConnector
from .query_executor import QueryExecutor
from .prompt_handler import SystemPromptHandler


class VectorStoreRAGService:
    """Complete RAG Service with API integration"""
    
    def __init__(self):
        print("🚀 Initializing Complete RAG Service...")
        self.groq_service = GroqService()
        self.vectorstore = VectorStoreService()
        self.db_connector = DatabaseConnector()
        self.query_executor = QueryExecutor()
        self.prompt_handler = SystemPromptHandler()
        
        self.query_cache = {}
        self._initialize_knowledge_base()
        
        print("✅ Complete RAG Service ready!")
    
    def _initialize_knowledge_base(self):
        """Initialize vector store with database knowledge + API data"""
        try:
            self.vectorstore.initialize_with_database_knowledge(refresh=False)
        except Exception as e:
            print(f"⚠️ Error initializing knowledge base: {e}")
    
    def process_query(
        self, 
        query: str, 
        user_context: Dict = None, 
        use_cache: bool = True,
        use_reranking: bool = True
    ) -> Dict:
        """Process query with complete RAG pipeline"""
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🔍 Processing Query: '{query}'")
        print(f"{'='*60}")
        
        try:
            # Step 1: Cache check
            if use_cache:
                cached = self._check_cache(query)
                if cached:
                    print("✅ Cache hit!")
                    cached['cached'] = True
                    cached['response_time'] = time.time() - start_time
                    return cached
            
            # Step 2: Detect query type
            query_type = self._classify_query(query)
            is_permission_query = self._is_permission_query(query)
            
            print(f"\n📊 Query Analysis:")
            print(f"   Type: {query_type}")
            print(f"   Permission query: {is_permission_query}")
            
            # Step 3: Query rewriting
            print("\n📝 Step 1: Query Rewriting")
            query_variations = self._rewrite_query(query)
            print(f"   Generated {len(query_variations)} variations")
            
            # Step 4: Vector search
            print("\n🔍 Step 2: Vector Search")
            search_results = self._multi_query_search(query_variations, k=15)
            print(f"   Retrieved {len(search_results)} documents")
            
            # Debug: Show top results
            if search_results:
                print("   Top 3 results:")
                for i, r in enumerate(search_results[:3], 1):
                    metadata = r.get('metadata', {})
                    print(f"     {i}. Type: {metadata.get('type')}, Source: {metadata.get('source', 'db')}, Score: {r.get('score', 0):.3f}")
            
            # Step 5: Check for API data in results
            has_api_data = any(
                r.get('metadata', {}).get('source') == 'api' 
                for r in search_results[:5]
            )
            
            print(f"   Has API data: {has_api_data}")
            
            # Step 6: Reranking
            if use_reranking and len(search_results) > 0:
                print("\n🎯 Step 3: Reranking")
                search_results = self._rerank_results(query, search_results, is_permission_query)
                print(f"   Top result score: {search_results[0].get('rerank_score', 0):.3f}")
            
            # Step 7: Extract database context (only for non-permission queries)
            db_context = {"tables_used": [], "schema_info": {}, "entity_types": []}
            db_query_results = None
            sql_executed = None
            
            if not is_permission_query:
                print("\n🗄️ Step 4: Database Context Extraction")
                db_context = self._extract_database_context(query, search_results)
                
                # Execute database query if needed
                if db_context.get("tables_used"):
                    print("\n💾 Step 5: Execute Database Query")
                    db_query_results, sql_executed = self._execute_database_query(
                        query, db_context
                    )
            else:
                print("\n⏭️ Skipping database query (permission query)")
            
            # Step 8: Build context
            print("\n📚 Step 6: Context Building")
            contexts = self._build_enhanced_context(
                query,
                search_results,
                db_context,
                db_query_results,
                is_permission_query
            )
            print(f"   Built {len(contexts)} context chunks")
            
            # Step 9: Context window management
            print("\n✂️ Step 7: Context Window Management")
            managed_contexts = self._manage_context_window(contexts, max_tokens=6000)
            print(f"   Using {len(managed_contexts)} context chunks")
            
            # Step 10: Create optimized system prompt
            print("\n🤖 Step 8: System Prompt Creation")
            system_prompt = self.prompt_handler.create_prompt(
                query=query,
                context_sources={},
                has_database_results=(db_query_results is not None),
                has_api_data=has_api_data
            )
            
            # Step 11: Generate response
            print("\n💬 Step 9: Response Generation")
            response_data = self.groq_service.generate_response(
                query=query,
                context=managed_contexts,
                system_prompt=system_prompt
            )
            
            response_time = time.time() - start_time
            
            # Step 12: Quality evaluation
            print("\n📊 Step 10: Quality Evaluation")
            quality_score = self._evaluate_response_quality(
                query,
                response_data.get("response", ""),
                search_results,
                db_query_results,
                has_api_data
            )
            print(f"   Quality Score: {quality_score:.2f}/5.0")
            
            # Prepare result
            result = {
                "query": query,
                "response": response_data.get("response", "No response generated"),
                "context_sources": {
                    "vector_store_results": len(search_results),
                    "has_api_data": has_api_data,
                    "database_tables_used": db_context.get("tables_used", []),
                    "sql_executed": sql_executed,
                    "database_results_count": len(db_query_results) if db_query_results else 0,
                    "response_method": "complete_rag_v4.0",
                    "query_type": query_type,
                    "is_permission_query": is_permission_query,
                    "quality_score": quality_score,
                    "top_sources": [
                        {
                            "type": r.get("metadata", {}).get("type", "unknown"),
                            "source": r.get("metadata", {}).get("source", "db"),
                            "entity": r.get("metadata", {}).get("entity", "unknown"),
                            "score": round(r.get("score", 0), 3)
                        }
                        for r in search_results[:3]
                    ]
                },
                "database_results": db_query_results[:10] if db_query_results else [],
                "tokens_used": response_data.get("tokens_used", 0),
                "response_time": round(response_time, 2),
                "success": response_data.get("success", True),
                "cached": False
            }
            
            # Cache result
            if use_cache and result['success']:
                self._cache_result(query, result)
            
            print(f"\n{'='*60}")
            print(f"✅ Query processed in {response_time:.2f}s")
            print(f"   API data used: {has_api_data}")
            print(f"   DB results: {len(db_query_results) if db_query_results else 0}")
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            
            return self._fallback_response(query, str(e), time.time() - start_time)
    
    def _is_permission_query(self, query: str) -> bool:
        """Check if query is about permissions/roles"""
        query_lower = query.lower()
        permission_keywords = [
            'permission', 'permissions', 'access', 'rights',
            'allowed', 'can do', 'able to', 'privileges',
            'what can', 'capabilities', 'role'
        ]
        return any(kw in query_lower for kw in permission_keywords)
    
    def _execute_database_query(
        self,
        query: str,
        db_context: Dict
    ) -> tuple:
        """Execute database query and return results + SQL"""
        
        tables_used = db_context.get("tables_used", [])
        schema_info = db_context.get("schema_info", {})
        
        if not tables_used or not schema_info:
            return None, None
        
        main_table = tables_used[0]
        
        if main_table not in schema_info:
            return None, None
        
        table_info = schema_info[main_table]
        table_context = {
            "table_name": main_table,
            "columns": table_info.get("columns", []),
            "entity_type": table_info.get("entity_type", "unknown"),
            "row_count": table_info.get("row_count", 0)
        }
        
        query_result = self.query_executor.execute_user_query(query, table_context)
        
        if query_result["success"]:
            return query_result["results"], query_result["sql"]
        else:
            return None, None
    
    def _build_enhanced_context(
        self,
        query: str,
        search_results: List[Dict],
        db_context: Dict,
        db_query_results: Optional[List[Dict]],
        is_permission_query: bool
    ) -> List[str]:
        """Build context with priority for API data in permission queries"""
        
        contexts = []
        
        # For permission queries, prioritize API data
        if is_permission_query:
            api_results = [
                r for r in search_results 
                if r.get('metadata', {}).get('source') == 'api'
            ]
            
            if api_results:
                print(f"   🎯 Found {len(api_results)} API data sources (high priority)")
                
                for i, result in enumerate(api_results[:5], 1):
                    content = result.get("content", "")
                    if len(content) > 2000:
                        content = content[:2000] + "..."
                    
                    metadata = result.get("metadata", {})
                    
                    context_str = f"""[🔴 ROLE/PERMISSION DATA - SOURCE {i} - PRIORITY: HIGH]
Type: {metadata.get('type', 'unknown')}
Role: {metadata.get('role_name', 'N/A')}

{content}

[END OF ROLE/PERMISSION DATA]
"""
                    contexts.append(context_str)
            else:
                print("   ⚠️ No API data found for permission query")
        
        # Add database results if available
        if db_query_results and len(db_query_results) > 0:
            print(f"   📊 Adding {len(db_query_results)} database results")
            
            results_context = self.query_executor.format_results_for_llm(
                db_query_results,
                query
            )
            
            contexts.insert(0, f"""[🔴 ACTUAL DATABASE QUERY RESULTS]

{results_context}

[END OF DATABASE RESULTS]
""")
        
        # Add other vector search results
        other_results = [
            r for r in search_results
            if r.get('metadata', {}).get('source') != 'api' or not is_permission_query
        ]
        
        for i, result in enumerate(other_results[:5], 1):
            content = result.get("content", "")
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            metadata = result.get("metadata", {})
            
            context_str = f"""[Source {i}]
Type: {metadata.get('type', 'unknown')}
{content}
"""
            contexts.append(context_str)
        
        return contexts
    
    def _rerank_results(
        self,
        query: str,
        results: List[Dict],
        is_permission_query: bool
    ) -> List[Dict]:
        """Rerank with boosting for API data in permission queries"""
        
        if not results:
            return results
        
        try:
            for result in results:
                score = 0.0
                
                # Base scores
                score += result.get('score', 0) * 0.4
                score += result.get('rrf_score', 0) * 0.3
                
                metadata = result.get('metadata', {})
                
                # Boost API data for permission queries
                if is_permission_query and metadata.get('source') == 'api':
                    score += 1.0  # Big boost!
                    print(f"   🚀 Boosting API result: {metadata.get('role_name', 'unknown')}")
                
                # Boost by priority
                priority = metadata.get('priority', 'medium')
                if priority == 'very_high':
                    score += 0.3
                elif priority == 'high':
                    score += 0.2
                
                # Boost by type
                if metadata.get('type') == 'role_permissions':
                    score += 0.2
                elif metadata.get('type') == 'role_summary':
                    score += 0.3  # Summaries are very useful
                
                result['rerank_score'] = score
            
            results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            
        except Exception as e:
            print(f"⚠️ Reranking failed: {e}")
        
        return results
    
    def _evaluate_response_quality(
        self,
        query: str,
        response: str,
        search_results: List[Dict],
        db_query_results: Optional[List[Dict]],
        has_api_data: bool
    ) -> float:
        """Evaluate response quality"""
        
        score = 3.0
        
        # Check for specific data usage
        if has_api_data:
            # For permission queries, check if response mentions specific permissions
            if any(word in response.lower() for word in ['read', 'create', 'update', 'delete']):
                score += 1.0
            else:
                score -= 0.5  # Penalty if API data available but not used
        
        if db_query_results:
            score += 0.5
            if any(word in response.lower() for word in ['there are', 'found', 'records']):
                score += 0.3
        
        # Check for speculation markers
        speculation_markers = [
            'typically', 'usually', 'may', 'might', 'could',
            'not available', 'would need access'
        ]
        if any(marker in response.lower() for marker in speculation_markers):
            score -= 0.8
        
        # Response length
        response_len = len(response.split())
        if 20 < response_len < 300:
            score += 0.3
        elif response_len < 10:
            score -= 0.5
        
        # Check for numbers (good for count queries)
        if any(char.isdigit() for char in response):
            score += 0.2
        
        return min(5.0, max(1.0, score))
    
    # Keep all other helper methods from previous version
    # (_rewrite_query, _multi_query_search, _reciprocal_rank_fusion,
    #  _manage_context_window, _extract_database_context, _classify_query,
    #  _check_cache, _cache_result, _fallback_response, get_database_summary)
    
    def _rewrite_query(self, query: str) -> List[str]:
        """Rewrite query"""
        variations = [query]
        if len(query.split()) < 3:
            return variations
        try:
            system_prompt = """Generate 3 alternatives:
1. Technical
2. Conversational  
3. Keywords
Output only 3 rewrites, one per line."""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Rewrite: {query}"}
            ]
            response = self.groq_service.client.chat.completions.create(
                model=self.groq_service.model,
                messages=messages,
                temperature=0.3,
                max_tokens=150
            )
            rewrites = response.choices[0].message.content.strip().split('\n')
            for rewrite in rewrites[:3]:
                cleaned = rewrite.strip().lstrip('123456789.').strip()
                if cleaned and len(cleaned) > 5:
                    variations.append(cleaned)
        except Exception as e:
            print(f"⚠️ Query rewriting failed: {e}")
        return variations
    
    def _multi_query_search(self, queries: List[str], k: int = 15) -> List[Dict]:
        """Multi-query search"""
        all_results = []
        seen_content = set()
        for i, query_var in enumerate(queries):
            try:
                results = self.vectorstore.search(query_var, k=k)
                for result in results:
                    content_hash = hashlib.md5(result.get('content', '')[:100].encode()).hexdigest()
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        result['query_variation'] = i
                        result['query_text'] = query_var
                        all_results.append(result)
            except Exception as e:
                print(f"⚠️ Search failed for '{query_var}': {e}")
        all_results = self._reciprocal_rank_fusion(all_results)
        all_results.sort(key=lambda x: x.get('rrf_score', 0), reverse=True)
        return all_results[:k]
    
    def _reciprocal_rank_fusion(self, results: List[Dict], k: int = 60) -> List[Dict]:
        """RRF"""
        content_scores = defaultdict(lambda: {'result': None, 'rrf_score': 0})
        for rank, result in enumerate(results, 1):
            content_hash = hashlib.md5(result.get('content', '')[:100].encode()).hexdigest()
            rrf_score = 1.0 / (k + rank)
            content_scores[content_hash]['rrf_score'] += rrf_score
            if content_scores[content_hash]['result'] is None:
                content_scores[content_hash]['result'] = result
        enhanced_results = []
        for content_hash, data in content_scores.items():
            result = data['result']
            result['rrf_score'] = data['rrf_score']
            enhanced_results.append(result)
        return enhanced_results
    
    def _manage_context_window(self, contexts: List[str], max_tokens: int = 6000) -> List[str]:
        """Manage context window"""
        selected = []
        total_chars = 0
        max_chars = max_tokens * 4
        for context in contexts:
            context_chars = len(context)
            if total_chars + context_chars < max_chars:
                selected.append(context)
                total_chars += context_chars
            else:
                remaining = max_chars - total_chars
                if remaining > 500:
                    selected.append(context[:remaining] + "...")
                break
        return selected
    
    def _extract_database_context(self, query: str, search_results: List[Dict]) -> Dict:
        """Extract database context"""
        tables_mentioned = set()
        entity_types = set()
        for result in search_results[:5]:
            metadata = result.get("metadata", {})
            if "table_name" in metadata:
                tables_mentioned.add(metadata["table_name"])
            if "main_table" in metadata:
                tables_mentioned.add(metadata["main_table"])
            if "entity" in metadata:
                entity_types.add(metadata["entity"])
        discovered_tables = self.db_connector.discover_relevant_tables(query)
        tables_mentioned.update(discovered_tables)
        schema_info = {}
        for table in list(tables_mentioned)[:3]:
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
    
    def _classify_query(self, query: str) -> str:
        """Classify query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ["permission", "role", "access"]):
            return "permission"
        elif any(word in query_lower for word in ["how many", "count", "total", "number of"]):
            return "counting"
        elif any(word in query_lower for word in ["show", "list", "display", "get all"]):
            return "listing"
        else:
            return "general"
    
    def _check_cache(self, query: str) -> Optional[Dict]:
        """Check cache"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return self.query_cache.get(query_hash)
    
    def _cache_result(self, query: str, result: Dict):
        """Cache result"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        self.query_cache[query_hash] = result
        if len(self.query_cache) > 1000:
            to_remove = list(self.query_cache.keys())[:100]
            for key in to_remove:
                del self.query_cache[key]
    
    def _fallback_response(self, query: str, error: str, elapsed_time: float) -> Dict:
        """Fallback"""
        return {
            "query": query,
            "response": f"I apologize, but I encountered an error processing your query.",
            "context_sources": {"response_method": "fallback", "error": error[:200]},
            "tokens_used": 0,
            "response_time": round(elapsed_time, 2),
            "success": False,
            "cached": False
        }
    
    def get_database_summary(self) -> Dict:
        """Database summary"""
        try:
            all_tables = self.db_connector.get_all_tables()
            user_tables = [t for t in all_tables if not any(
                skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']
            )]
            return {
                "total_tables": len(all_tables),
                "user_tables": len(user_tables),
                "sample_tables": user_tables[:20]
            }
        except Exception as e:
            return {"error": str(e)}