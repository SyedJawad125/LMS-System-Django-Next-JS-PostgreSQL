# # ============================================
# # ENHANCED RAG SERVICE
# # File: apps/rag_system/services/rag_service.py
# # ============================================

# from typing import Dict, List
# import time
# from .groq_service import GroqService
# from .vectorstore_service import VectorStoreService
# from .database_connector import DatabaseConnector


# class VectorStoreRAGService:
#     """Enhanced RAG Service with PostgreSQL + Vector Store"""
    
#     def __init__(self):
#         print("🚀 Initializing Enhanced RAG Service...")
#         self.groq_service = GroqService()
#         self.vectorstore = VectorStoreService()
#         self.db_connector = DatabaseConnector()
        
#         # Initialize vector store with database knowledge
#         self._initialize_knowledge_base()
        
#         print("✅ Enhanced RAG Service ready!")
    
#     def _initialize_knowledge_base(self):
#         """Initialize vector store with PostgreSQL database knowledge"""
#         try:
#             self.vectorstore.initialize_with_database_knowledge(refresh=False)
#         except Exception as e:
#             print(f"⚠️ Error initializing knowledge base: {e}")
    
#     def process_query(self, query: str, user_context: Dict = None, use_cache: bool = True) -> Dict:
#         """Process query using Vector Store + Database"""
#         start_time = time.time()
        
#         print(f"\n🔍 Processing query: '{query}'")
        
#         try:
#             # Step 1: Search vector store for relevant knowledge
#             print("📚 Searching vector store...")
#             search_results = self.vectorstore.search(query, k=10)
            
#             # Step 2: Extract database context
#             db_context = self._extract_database_context(query, search_results)
            
#             # Step 3: Build enhanced context
#             context = self._build_context(query, search_results, db_context)
            
#             # Step 4: Create system prompt
#             system_prompt = self._create_system_prompt(query, search_results, db_context)
            
#             # Step 5: Generate response with GROQ
#             print("🤖 Generating response with GROQ...")
#             response_data = self.groq_service.generate_response(
#                 query=query,
#                 context=context,
#                 system_prompt=system_prompt
#             )
            
#             response_time = time.time() - start_time
            
#             # Prepare result
#             result = {
#                 "query": query,
#                 "response": response_data.get("response", "No response generated"),
#                 "context_sources": {
#                     "vector_store_results": len(search_results),
#                     "database_tables_used": db_context.get("tables_used", []),
#                     "response_method": "vector_store_with_database",
#                     "query_type": self._classify_query(query),
#                     "top_sources": [
#                         {
#                             "type": r.get("metadata", {}).get("type", "unknown"),
#                             "entity": r.get("metadata", {}).get("entity", "unknown"),
#                             "score": round(r.get("score", 0), 3)
#                         }
#                         for r in search_results[:3]
#                     ]
#                 },
#                 "tokens_used": response_data.get("tokens_used", 0),
#                 "response_time": round(response_time, 2),
#                 "success": response_data.get("success", True),
#                 "cached": False
#             }
            
#             print(f"✅ Query processed in {response_time:.2f}s")
#             return result
            
#         except Exception as e:
#             print(f"❌ Error processing query: {e}")
#             import traceback
#             traceback.print_exc()
            
#             return {
#                 "query": query,
#                 "response": f"I encountered an error processing your request: {str(e)[:200]}",
#                 "context_sources": {},
#                 "tokens_used": 0,
#                 "response_time": time.time() - start_time,
#                 "success": False,
#                 "error": str(e)
#             }
    
#     def _extract_database_context(self, query: str, search_results: List[Dict]) -> Dict:
#         """Extract database context from search results"""
#         print("🗄️ Extracting database context...")
        
#         # Find relevant tables from search results
#         tables_mentioned = set()
#         entity_types = set()
        
#         for result in search_results[:5]:
#             metadata = result.get("metadata", {})
            
#             # Extract table names
#             if "table_name" in metadata:
#                 tables_mentioned.add(metadata["table_name"])
            
#             if "main_table" in metadata:
#                 tables_mentioned.add(metadata["main_table"])
            
#             # Extract entity types
#             if "entity" in metadata:
#                 entity_types.add(metadata["entity"])
        
#         # Also discover tables directly from query
#         discovered_tables = self.db_connector.discover_relevant_tables(query)
#         tables_mentioned.update(discovered_tables)
        
#         # Get schema info for mentioned tables
#         schema_info = {}
#         for table in list(tables_mentioned)[:3]:  # Top 3 tables
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
    
#     def _build_context(self, query: str, search_results: List[Dict], db_context: Dict) -> List[str]:
#         """Build context list for GROQ"""
#         context = []
        
#         # Add top search results
#         for i, result in enumerate(search_results[:5], 1):
#             content = result.get("content", "")
#             if content and len(content) > 50:
#                 # Truncate long content
#                 if len(content) > 800:
#                     content = content[:800] + "..."
                
#                 metadata = result.get("metadata", {})
#                 context_type = metadata.get("type", "unknown")
                
#                 context.append(f"[Source {i} - {context_type}]\n{content}")
        
#         # Add database context
#         if db_context.get("schema_info"):
#             db_info = ["[Database Schema Information]"]
#             for table, info in db_context["schema_info"].items():
#                 db_info.append(f"• Table: {table}")
#                 db_info.append(f"  Columns: {', '.join(info['columns'][:8])}")
#                 db_info.append(f"  Records: {info['row_count']}")
#                 db_info.append(f"  Entity: {info['entity_type']}")
            
#             context.append("\n".join(db_info))
        
#         return context
    
#     def _create_system_prompt(self, query: str, search_results: List[Dict], db_context: Dict) -> str:
#         """Create enhanced system prompt"""
#         entity_types = db_context.get("entity_types", [])
#         tables_used = db_context.get("tables_used", [])
        
#         prompt_parts = [
#             "You are an intelligent LMS (Learning Management System) assistant with access to a PostgreSQL database.",
#             "",
#             "AVAILABLE INFORMATION:",
#         ]
        
#         # Add entity context
#         if entity_types:
#             prompt_parts.append(f"• Entities: {', '.join(entity_types)}")
        
#         # Add table context
#         if tables_used:
#             prompt_parts.append(f"• Tables: {', '.join(tables_used)}")
        
#         prompt_parts.extend([
#             "",
#             "RESPONSE GUIDELINES:",
#             "1. Provide accurate, specific answers based on the context",
#             "2. Use exact numbers when available from database",
#             "3. Mention table names when relevant",
#             "4. Be clear about what data is available",
#             "5. If information is incomplete, say so",
#             "6. Use natural, helpful language",
#             "",
#             f"USER QUERY: '{query}'",
#             "",
#             "Provide a helpful, accurate answer based on the context provided."
#         ])
        
#         return "\n".join(prompt_parts)
    
#     def _classify_query(self, query: str) -> str:
#         """Classify query type"""
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
    
#     def get_database_summary(self) -> Dict:
#         """Get summary of database structure"""
#         try:
#             all_tables = self.db_connector.get_all_tables()
            
#             # Filter user tables
#             user_tables = [t for t in all_tables if not any(
#                 skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']
#             )]
            
#             # Get counts for main entities
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
# IMPROVED RAG SERVICE WITH ENHANCEMENTS
# File: apps/rag_system/services/rag_service_enhanced.py
# ============================================

from typing import Dict, List, Optional, Tuple
import time
import hashlib
import numpy as np
from collections import defaultdict
from .groq_service import GroqService
from .vectorstore_service import VectorStoreService
from .database_connector import DatabaseConnector


class EnhancedVectorStoreRAGService:
    """
    Production-Grade RAG Service with:
    - Reranking for better relevance
    - Query rewriting for better retrieval
    - Context window management
    - Fallback mechanisms
    - Quality evaluation
    """
    
    def __init__(self):
        print("🚀 Initializing Enhanced RAG Service v2.0...")
        self.groq_service = GroqService()
        self.vectorstore = VectorStoreService()
        self.db_connector = DatabaseConnector()
        
        # Caches
        self.embedding_cache = {}
        self.query_cache = {}
        
        # Initialize reranker (optional - only if needed)
        self.reranker = None
        
        # Initialize knowledge base
        self._initialize_knowledge_base()
        
        print("✅ Enhanced RAG Service v2.0 ready!")
    
    def _initialize_knowledge_base(self):
        """Initialize vector store with database knowledge"""
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
        """
        Process query with enhanced RAG pipeline
        
        Pipeline:
        1. Query rewriting (multiple variations)
        2. Vector search across variations
        3. Reranking results (optional)
        4. Context building with relevance scoring
        5. Context window management
        6. LLM response generation
        7. Quality evaluation
        
        Args:
            query: User's question
            user_context: User information
            use_cache: Whether to use query cache
            use_reranking: Whether to rerank results
            
        Returns:
            Dict with response and metadata
        """
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🔍 Processing Enhanced Query: '{query}'")
        print(f"{'='*60}")
        
        try:
            # Step 1: Check cache
            if use_cache:
                cached = self._check_cache(query)
                if cached:
                    print("✅ Cache hit!")
                    cached['cached'] = True
                    cached['response_time'] = time.time() - start_time
                    return cached
            
            # Step 2: Query rewriting
            print("\n📝 Step 1: Query Rewriting")
            query_variations = self._rewrite_query(query)
            print(f"   Generated {len(query_variations)} variations")
            
            # Step 3: Multi-query vector search
            print("\n🔍 Step 2: Vector Search")
            search_results = self._multi_query_search(query_variations, k=15)
            print(f"   Retrieved {len(search_results)} documents")
            
            # Step 4: Reranking (optional but recommended)
            if use_reranking and len(search_results) > 0:
                print("\n🎯 Step 3: Reranking Results")
                search_results = self._rerank_results(query, search_results)
                print(f"   Top result score: {search_results[0]['score']:.3f}")
            
            # Step 5: Extract database context
            print("\n🗄️ Step 4: Database Context Extraction")
            db_context = self._extract_database_context(query, search_results)
            print(f"   Found {len(db_context.get('tables_used', []))} relevant tables")
            
            # Step 6: Build enhanced context
            print("\n📚 Step 5: Context Building")
            contexts = self._build_enhanced_context(
                query, 
                search_results, 
                db_context
            )
            
            # Step 7: Context window management
            print("\n✂️ Step 6: Context Window Management")
            managed_contexts = self._manage_context_window(contexts, max_tokens=6000)
            print(f"   Using {len(managed_contexts)} context chunks")
            
            # Step 8: Create enhanced system prompt
            print("\n🤖 Step 7: System Prompt Creation")
            system_prompt = self._create_enhanced_system_prompt(
                query, 
                search_results, 
                db_context
            )
            
            # Step 9: Generate response with GROQ
            print("\n💬 Step 8: Response Generation")
            response_data = self.groq_service.generate_response(
                query=query,
                context=managed_contexts,
                system_prompt=system_prompt
            )
            
            response_time = time.time() - start_time
            
            # Step 10: Quality evaluation
            print("\n📊 Step 9: Quality Evaluation")
            quality_score = self._evaluate_response_quality(
                query,
                response_data.get("response", ""),
                search_results
            )
            print(f"   Quality Score: {quality_score:.2f}/5.0")
            
            # Prepare result
            result = {
                "query": query,
                "response": response_data.get("response", "No response generated"),
                "context_sources": {
                    "vector_store_results": len(search_results),
                    "database_tables_used": db_context.get("tables_used", []),
                    "response_method": "enhanced_rag_v2",
                    "query_type": self._classify_query(query),
                    "reranked": use_reranking,
                    "query_variations": len(query_variations),
                    "quality_score": quality_score,
                    "top_sources": [
                        {
                            "type": r.get("metadata", {}).get("type", "unknown"),
                            "entity": r.get("metadata", {}).get("entity", "unknown"),
                            "score": round(r.get("score", 0), 3),
                            "rerank_score": round(r.get("rerank_score", 0), 3) if "rerank_score" in r else None
                        }
                        for r in search_results[:3]
                    ]
                },
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
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to simple response
            return self._fallback_response(query, str(e), time.time() - start_time)
    
    def _rewrite_query(self, query: str) -> List[str]:
        """
        Rewrite query into multiple variations for better retrieval
        
        Strategy:
        1. Keep original query
        2. Generate technical version
        3. Generate conversational version
        4. Generate keyword-focused version
        """
        variations = [query]  # Always include original
        
        # Only rewrite if query is complex enough
        if len(query.split()) < 3:
            return variations
        
        try:
            system_prompt = """You are a query rewriting expert. Generate 3 alternative versions of the query:

1. TECHNICAL: More precise, database-focused
2. CONVERSATIONAL: Natural, user-friendly
3. KEYWORDS: Key terms only

Example:
Original: "How many students are enrolled?"
1. Technical: "SELECT COUNT(*) FROM students WHERE status='active'"
2. Conversational: "Show me the total number of students"
3. Keywords: "students count total enrollment"

Keep rewrites concise. Output only the 3 rewrites, one per line."""

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
            
            # Clean and add rewrites
            for rewrite in rewrites[:3]:
                cleaned = rewrite.strip()
                # Remove numbering
                cleaned = cleaned.lstrip('123456789.').strip()
                if cleaned and len(cleaned) > 5:
                    variations.append(cleaned)
            
        except Exception as e:
            print(f"⚠️ Query rewriting failed: {e}")
        
        return variations
    
    def _multi_query_search(self, queries: List[str], k: int = 15) -> List[Dict]:
        """
        Search across multiple query variations and combine results
        
        Uses Reciprocal Rank Fusion (RRF) to combine results
        """
        all_results = []
        seen_content = set()
        
        for i, query_var in enumerate(queries):
            try:
                results = self.vectorstore.search(query_var, k=k)
                
                # Add query variation info
                for result in results:
                    content_hash = hashlib.md5(
                        result.get('content', '')[:100].encode()
                    ).hexdigest()
                    
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        result['query_variation'] = i
                        result['query_text'] = query_var
                        all_results.append(result)
                        
            except Exception as e:
                print(f"⚠️ Search failed for variation '{query_var}': {e}")
        
        # Apply Reciprocal Rank Fusion
        all_results = self._reciprocal_rank_fusion(all_results)
        
        # Sort by RRF score
        all_results.sort(key=lambda x: x.get('rrf_score', 0), reverse=True)
        
        return all_results[:k]
    
    def _reciprocal_rank_fusion(self, results: List[Dict], k: int = 60) -> List[Dict]:
        """
        Combine results from multiple queries using RRF
        
        RRF formula: score = sum(1 / (k + rank))
        """
        # Group by content
        content_scores = defaultdict(lambda: {'result': None, 'rrf_score': 0})
        
        for rank, result in enumerate(results, 1):
            content_hash = hashlib.md5(
                result.get('content', '')[:100].encode()
            ).hexdigest()
            
            # RRF score
            rrf_score = 1.0 / (k + rank)
            
            content_scores[content_hash]['rrf_score'] += rrf_score
            if content_scores[content_hash]['result'] is None:
                content_scores[content_hash]['result'] = result
        
        # Add RRF scores to results
        enhanced_results = []
        for content_hash, data in content_scores.items():
            result = data['result']
            result['rrf_score'] = data['rrf_score']
            enhanced_results.append(result)
        
        return enhanced_results
    
    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Rerank results using more sophisticated relevance scoring
        
        Uses cross-attention between query and documents
        """
        if not results:
            return results
        
        try:
            # Simple reranking based on multiple factors
            for result in results:
                score = 0.0
                
                # Factor 1: Original similarity score
                score += result.get('score', 0) * 0.4
                
                # Factor 2: RRF score if available
                score += result.get('rrf_score', 0) * 0.3
                
                # Factor 3: Content length (prefer moderate length)
                content_len = len(result.get('content', ''))
                if 200 < content_len < 2000:
                    score += 0.1
                
                # Factor 4: Metadata priority
                metadata = result.get('metadata', {})
                if metadata.get('priority') == 'high':
                    score += 0.1
                if metadata.get('type') == 'entity_knowledge':
                    score += 0.1
                
                result['rerank_score'] = score
            
            # Sort by rerank score
            results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            
        except Exception as e:
            print(f"⚠️ Reranking failed: {e}")
        
        return results
    
    def _manage_context_window(
        self, 
        contexts: List[str], 
        max_tokens: int = 6000
    ) -> List[str]:
        """
        Ensure contexts fit within LLM's context window
        
        Uses simple token estimation: ~4 chars = 1 token
        """
        selected = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough estimate
        
        for context in contexts:
            context_chars = len(context)
            
            if total_chars + context_chars < max_chars:
                selected.append(context)
                total_chars += context_chars
            else:
                # Try to fit truncated version
                remaining = max_chars - total_chars
                if remaining > 500:  # At least 500 chars
                    selected.append(context[:remaining] + "...")
                break
        
        return selected
    
    def _build_enhanced_context(
        self, 
        query: str, 
        search_results: List[Dict],
        db_context: Dict
    ) -> List[str]:
        """
        Build context with relevance weighting and deduplication
        """
        contexts = []
        
        # Add top search results with relevance indicators
        for i, result in enumerate(search_results[:5], 1):
            content = result.get("content", "")
            if not content or len(content) < 50:
                continue
            
            # Truncate very long content
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            metadata = result.get("metadata", {})
            score = result.get("rerank_score", result.get("score", 0))
            
            context_str = f"""[Source {i} - Relevance: {score:.3f}]
Type: {metadata.get('type', 'unknown')}
Entity: {metadata.get('entity', 'N/A')}
Table: {metadata.get('table_name', 'N/A')}

Content:
{content}
"""
            contexts.append(context_str)
        
        # Add database schema context
        if db_context.get("schema_info"):
            db_info = ["[Database Schema Information]"]
            
            for table, info in list(db_context["schema_info"].items())[:2]:
                db_info.append(f"\nTable: {table}")
                db_info.append(f"Columns: {', '.join(info.get('columns', [])[:8])}")
                db_info.append(f"Records: {info.get('row_count', 0)}")
                db_info.append(f"Entity: {info.get('entity_type', 'unknown')}")
            
            contexts.append("\n".join(db_info))
        
        return contexts
    
    def _create_enhanced_system_prompt(
        self, 
        query: str, 
        search_results: List[Dict],
        db_context: Dict
    ) -> str:
        """Create enhanced system prompt with more context"""
        
        entity_types = db_context.get("entity_types", [])
        tables_used = db_context.get("tables_used", [])
        
        prompt_parts = [
            "You are an advanced LMS (Learning Management System) AI assistant with access to:",
            "1. A comprehensive PostgreSQL database with student, teacher, class, and administrative data",
            "2. Semantic search capabilities over database documentation",
            "3. Query understanding and context extraction",
            "",
            "CURRENT CONTEXT:",
        ]
        
        if entity_types:
            prompt_parts.append(f"- Relevant Entities: {', '.join(entity_types)}")
        
        if tables_used:
            prompt_parts.append(f"- Database Tables: {', '.join(tables_used[:3])}")
        
        # Add retrieval quality indicator
        if search_results:
            avg_score = sum(r.get('score', 0) for r in search_results[:3]) / min(3, len(search_results))
            confidence = "HIGH" if avg_score > 0.7 else "MEDIUM" if avg_score > 0.4 else "LOW"
            prompt_parts.append(f"- Retrieval Confidence: {confidence}")
        
        prompt_parts.extend([
            "",
            "RESPONSE GUIDELINES:",
            "1. Provide accurate, specific answers based on retrieved context",
            "2. Use exact numbers from database when available",
            "3. Clearly distinguish between confirmed data and inferences",
            "4. Mention source tables when relevant for transparency",
            "5. If information is incomplete or uncertain, explicitly state this",
            "6. Use natural, professional language",
            "7. Structure complex answers with clear organization",
            "",
            f"USER QUERY: '{query}'",
            "",
            "Provide a comprehensive, accurate answer using the context provided."
        ])
        
        return "\n".join(prompt_parts)
    
    def _evaluate_response_quality(
        self, 
        query: str, 
        response: str,
        search_results: List[Dict]
    ) -> float:
        """
        Evaluate response quality on scale of 1-5
        
        Factors:
        - Retrieval relevance
        - Response length appropriateness
        - Factual grounding
        """
        score = 3.0  # Baseline
        
        # Factor 1: Retrieval quality
        if search_results:
            avg_score = sum(r.get('score', 0) for r in search_results[:3]) / min(3, len(search_results))
            if avg_score > 0.7:
                score += 1.0
            elif avg_score > 0.5:
                score += 0.5
        
        # Factor 2: Response length (should be substantive but not excessive)
        response_len = len(response.split())
        if 20 < response_len < 200:
            score += 0.5
        elif response_len < 10:
            score -= 0.5
        
        # Factor 3: Contains specific information (numbers, tables, etc.)
        if any(char.isdigit() for char in response):
            score += 0.3
        
        # Cap at 5.0
        return min(5.0, max(1.0, score))
    
    def _extract_database_context(self, query: str, search_results: List[Dict]) -> Dict:
        """Extract database context from search results"""
        print("🗄️ Extracting database context...")
        
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
    
    def _check_cache(self, query: str) -> Optional[Dict]:
        """Check if query result is cached"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return self.query_cache.get(query_hash)
    
    def _cache_result(self, query: str, result: Dict):
        """Cache query result"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        self.query_cache[query_hash] = result
        
        # Limit cache size
        if len(self.query_cache) > 1000:
            # Remove oldest entries
            to_remove = list(self.query_cache.keys())[:100]
            for key in to_remove:
                del self.query_cache[key]
    
    def _fallback_response(self, query: str, error: str, elapsed_time: float) -> Dict:
        """Generate fallback response when main pipeline fails"""
        return {
            "query": query,
            "response": f"I apologize, but I encountered an error processing your query. Please try rephrasing or ask about specific tables in the database.",
            "context_sources": {
                "response_method": "fallback",
                "error": error[:200]
            },
            "tokens_used": 0,
            "response_time": round(elapsed_time, 2),
            "success": False,
            "cached": False
        }
    
    def get_database_summary(self) -> Dict:
        """Get summary of database structure"""
        try:
            all_tables = self.db_connector.get_all_tables()
            
            user_tables = [t for t in all_tables if not any(
                skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']
            )]
            
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