# ============================================
# IMPROVED QUERY PROCESSOR
# File: apps/rag_system/services/improved_query_processor.py
# ============================================

"""
Better query understanding and SQL generation.
Key improvements:
1. Intent classification
2. Entity extraction
3. Context-aware SQL generation
4. Query validation
"""

import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class QueryIntent(Enum):
    """Query intent types"""
    COUNT = "count"
    LIST = "list"
    SEARCH = "search"
    AGGREGATE = "aggregate"
    PERMISSION = "permission"
    RELATIONSHIP = "relationship"
    CONVERSATIONAL = "conversational"
    UNKNOWN = "unknown"


class ImprovedQueryProcessor:
    """Process queries with better understanding"""
    
    def __init__(self, groq_service, db_connector):
        self.groq = groq_service
        self.db = db_connector
        
        # Intent patterns
        self.intent_patterns = {
            QueryIntent.COUNT: [
                r'how many', r'count', r'number of', r'total',
                r'how much', r'quantity'
            ],
            QueryIntent.LIST: [
                r'list', r'show', r'display', r'get all',
                r'what are', r'give me'
            ],
            QueryIntent.SEARCH: [
                r'find', r'search', r'lookup', r'get',
                r'where is', r'who is'
            ],
            QueryIntent.AGGREGATE: [
                r'average', r'sum', r'max', r'min',
                r'statistics', r'total'
            ],
            QueryIntent.PERMISSION: [
                r'permission', r'access', r'rights', r'can',
                r'allowed', r'capabilities', r'what can'
            ],
            QueryIntent.RELATIONSHIP: [
                r'relationship', r'connected', r'related',
                r'belongs to', r'associated with'
            ],
            QueryIntent.CONVERSATIONAL: [
                r'hello', r'hi', r'thanks', r'help',
                r'what can you do', r'how are you'
            ]
        }
        
        # Entity keywords
        self.entity_keywords = {
            'student': ['student', 'pupil', 'learner'],
            'teacher': ['teacher', 'instructor', 'faculty'],
            'user': ['user', 'account', 'profile'],
            'class': ['class', 'grade', 'section'],
            'exam': ['exam', 'test', 'assessment'],
            'attendance': ['attendance', 'presence', 'absence'],
            'fee': ['fee', 'payment', 'invoice'],
            'role': ['role', 'permission', 'access'],
            'parent': ['parent', 'guardian'],
            'subject': ['subject', 'course'],
            'assignment': ['assignment', 'homework'],
            'vehicle': ['vehicle', 'bus', 'transport'],
            'employee': ['employee', 'staff']
        }
    
    def analyze_query(self, query: str, vector_results: List[Dict]) -> Dict:
        """
        Comprehensive query analysis
        
        Returns:
            {
                'intent': QueryIntent,
                'entities': List[str],
                'filters': Dict,
                'needs_join': bool,
                'tables': List[str],
                'confidence': float
            }
        """
        
        query_lower = query.lower()
        
        # 1. Classify intent
        intent = self._classify_intent(query_lower)
        
        # 2. Extract entities
        entities = self._extract_entities(query_lower)
        
        # 3. Extract filters
        filters = self._extract_filters(query_lower)
        
        # 4. Determine tables from entities + vector results
        tables = self._determine_tables(entities, vector_results)
        
        # 5. Check if JOIN needed
        needs_join = len(tables) > 1 or self._check_join_indicators(query_lower)
        
        # 6. Calculate confidence
        confidence = self._calculate_confidence(intent, entities, tables, vector_results)
        
        return {
            'intent': intent,
            'entities': entities,
            'filters': filters,
            'tables': tables,
            'needs_join': needs_join,
            'confidence': confidence,
            'query_lower': query_lower
        }
    
    def _classify_intent(self, query_lower: str) -> QueryIntent:
        """Classify query intent"""
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return QueryIntent.UNKNOWN
    
    def _extract_entities(self, query_lower: str) -> List[str]:
        """Extract entities from query"""
        
        entities = []
        
        for entity, keywords in self.entity_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if entity not in entities:
                        entities.append(entity)
                    break
        
        return entities
    
    def _extract_filters(self, query_lower: str) -> Dict:
        """Extract filter conditions from query"""
        
        filters = {}
        
        # Name filter
        name_match = re.search(r'named? ["\']?(\w+)["\']?', query_lower)
        if name_match:
            filters['name'] = name_match.group(1)
        
        # Email filter
        email_match = re.search(r'email (\S+@\S+)', query_lower)
        if email_match:
            filters['email'] = email_match.group(1)
        
        # Status filter
        if 'active' in query_lower:
            filters['status'] = 'active'
        elif 'inactive' in query_lower:
            filters['status'] = 'inactive'
        
        # Date filters
        if 'today' in query_lower:
            filters['date'] = 'today'
        elif 'this week' in query_lower:
            filters['date'] = 'this_week'
        elif 'this month' in query_lower:
            filters['date'] = 'this_month'
        
        # Numeric filters
        greater_match = re.search(r'(?:greater than|more than|above)\s+(\d+)', query_lower)
        if greater_match:
            filters['greater_than'] = int(greater_match.group(1))
        
        less_match = re.search(r'(?:less than|fewer than|below)\s+(\d+)', query_lower)
        if less_match:
            filters['less_than'] = int(less_match.group(1))
        
        return filters
    
    def _determine_tables(self, entities: List[str], vector_results: List[Dict]) -> List[str]:
        """Determine which tables to query"""
        
        tables = set()
        
        # From entities
        for entity in entities:
            table = self.db.get_actual_table_name(entity)
            if table:
                tables.add(table)
        
        # From vector results metadata
        for result in vector_results[:5]:
            metadata = result.get('metadata', {})
            
            if 'table' in metadata:
                tables.add(metadata['table'])
            
            if 'main_table' in metadata:
                tables.add(metadata['main_table'])
            
            if 'mentioned_tables' in metadata:
                tables.update(metadata['mentioned_tables'][:2])
        
        return list(tables)
    
    def _check_join_indicators(self, query_lower: str) -> bool:
        """Check if query needs JOIN"""
        
        join_indicators = [
            'with', 'and', 'having', 'in',
            'enrolled in', 'taught by', 'assigned to',
            'belongs to', 'related to'
        ]
        
        return any(indicator in query_lower for indicator in join_indicators)
    
    def _calculate_confidence(
        self,
        intent: QueryIntent,
        entities: List[str],
        tables: List[str],
        vector_results: List[Dict]
    ) -> float:
        """Calculate confidence score"""
        
        confidence = 0.5  # Base confidence
        
        # Boost for clear intent
        if intent != QueryIntent.UNKNOWN:
            confidence += 0.2
        
        # Boost for recognized entities
        if entities:
            confidence += 0.15 * min(1, len(entities) / 2)
        
        # Boost for found tables
        if tables:
            confidence += 0.15 * min(1, len(tables) / 2)
        
        # Boost for high-quality vector results
        if vector_results:
            top_score = vector_results[0].get('final_score', 0)
            confidence += 0.2 * top_score
        
        return min(1.0, confidence)
    
    def generate_sql(
        self,
        query: str,
        analysis: Dict,
        vector_results: List[Dict]
    ) -> Optional[str]:
        """
        Generate SQL based on comprehensive analysis
        """
        
        intent = analysis['intent']
        entities = analysis['entities']
        filters = analysis['filters']
        tables = analysis['tables']
        
        if not tables:
            return None
        
        main_table = tables[0]
        
        # Get table schema
        schema = self.db.get_table_schema_info(main_table)
        columns = schema.get('columns', [])
        
        # Build SQL based on intent
        if intent == QueryIntent.COUNT:
            sql = self._generate_count_sql(main_table, filters, columns)
        
        elif intent == QueryIntent.LIST:
            sql = self._generate_list_sql(main_table, filters, columns, analysis)
        
        elif intent == QueryIntent.SEARCH:
            sql = self._generate_search_sql(main_table, filters, columns, analysis)
        
        elif intent == QueryIntent.AGGREGATE:
            sql = self._generate_aggregate_sql(main_table, filters, columns, analysis)
        
        else:
            # Default: list query
            sql = self._generate_list_sql(main_table, filters, columns, analysis)
        
        return sql
    
    def _generate_count_sql(
        self,
        table: str,
        filters: Dict,
        columns: List[str]
    ) -> str:
        """Generate COUNT query"""
        
        where_clauses = ["deleted = false"]
        
        # Add filters
        if 'status' in filters:
            if 'is_active' in columns:
                where_clauses.append(f"is_active = {filters['status'] == 'active'}")
        
        where_str = " AND ".join(where_clauses)
        
        return f"SELECT COUNT(*) as count FROM {table} WHERE {where_str}"
    
    def _generate_list_sql(
        self,
        table: str,
        filters: Dict,
        columns: List[str],
        analysis: Dict
    ) -> str:
        """Generate LIST query"""
        
        # Select columns
        select_cols = "*"
        
        # Build WHERE clause
        where_clauses = ["deleted = false"]
        
        if 'name' in filters and 'name' in columns:
            where_clauses.append(f"name ILIKE '%{filters['name']}%'")
        
        if 'email' in filters and 'email' in columns:
            where_clauses.append(f"email ILIKE '%{filters['email']}%'")
        
        if 'status' in filters and 'is_active' in columns:
            where_clauses.append(f"is_active = {filters['status'] == 'active'}")
        
        where_str = " AND ".join(where_clauses)
        
        # Add LIMIT
        limit = 100
        
        return f"SELECT {select_cols} FROM {table} WHERE {where_str} LIMIT {limit}"
    
    def _generate_search_sql(
        self,
        table: str,
        filters: Dict,
        columns: List[str],
        analysis: Dict
    ) -> str:
        """Generate SEARCH query"""
        
        # Similar to list but with more specific WHERE clauses
        return self._generate_list_sql(table, filters, columns, analysis)
    
    def _generate_aggregate_sql(
        self,
        table: str,
        filters: Dict,
        columns: List[str],
        analysis: Dict
    ) -> str:
        """Generate AGGREGATE query"""
        
        query_lower = analysis['query_lower']
        
        # Determine aggregate function
        if 'average' in query_lower or 'avg' in query_lower:
            agg_func = 'AVG'
        elif 'sum' in query_lower or 'total' in query_lower:
            agg_func = 'SUM'
        elif 'max' in query_lower or 'maximum' in query_lower:
            agg_func = 'MAX'
        elif 'min' in query_lower or 'minimum' in query_lower:
            agg_func = 'MIN'
        else:
            agg_func = 'COUNT'
        
        # Find numeric column (if needed)
        numeric_col = None
        for col in columns:
            if 'amount' in col or 'count' in col or 'rate' in col:
                numeric_col = col
                break
        
        where_clauses = ["deleted = false"]
        where_str = " AND ".join(where_clauses)
        
        if agg_func == 'COUNT':
            return f"SELECT COUNT(*) as result FROM {table} WHERE {where_str}"
        elif numeric_col:
            return f"SELECT {agg_func}({numeric_col}) as result FROM {table} WHERE {where_str}"
        else:
            return f"SELECT COUNT(*) as result FROM {table} WHERE {where_str}"
    
    def validate_and_fix_sql(self, sql: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate SQL and suggest fixes
        
        Returns:
            (is_valid, error_message, fixed_sql)
        """
        
        if not sql:
            return (False, "No SQL generated", None)
        
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return (False, "Only SELECT queries allowed", None)
        
        # Check for dangerous commands
        dangerous = ['DELETE FROM', 'DROP TABLE', 'UPDATE', 'INSERT INTO', 'TRUNCATE']
        for danger in dangerous:
            if danger in sql_upper:
                return (False, f"Forbidden command: {danger}", None)
        
        # Check for deleted filter
        if 'deleted' not in sql.lower():
            # Add deleted filter
            if 'WHERE' in sql_upper:
                fixed_sql = sql.replace('WHERE', 'WHERE deleted = false AND', 1)
            else:
                # Add WHERE clause before LIMIT or at end
                if 'LIMIT' in sql_upper:
                    fixed_sql = sql.replace('LIMIT', 'WHERE deleted = false LIMIT', 1)
                else:
                    fixed_sql = sql + ' WHERE deleted = false'
            
            return (True, "Added deleted filter", fixed_sql)
        
        return (True, "Valid", sql)


# ============================================
# INTEGRATION WITH RAG SERVICE
# ============================================

class EnhancedRAGService:
    """RAG service with improved query processing"""
    
    def __init__(self):
        from .groq_service import GroqService
        from .database_connector import DatabaseConnector
        from .optimized_vectorstore import OptimizedVectorStore
        
        self.groq = GroqService()
        self.db = DatabaseConnector()
        self.vectorstore = OptimizedVectorStore()
        self.query_processor = ImprovedQueryProcessor(self.groq, self.db)
    
    def process_query(self, query: str, user_context: Dict = None) -> Dict:
        """Process query with improved understanding"""
        
        import time
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"🔍 Processing: '{query}'")
        print(f"{'='*80}")
        
        # 1. Vector search
        print("\n📚 Step 1: Vector Search")
        vector_results = self.vectorstore.search(query, k=10)
        print(f"   Retrieved {len(vector_results)} results")
        
        if vector_results:
            top_result = vector_results[0]
            print(f"   Top result: {top_result['metadata'].get('type')} (score: {top_result['final_score']:.3f})")
        
        # 2. Analyze query
        print("\n🧠 Step 2: Query Analysis")
        analysis = self.query_processor.analyze_query(query, vector_results)
        
        print(f"   Intent: {analysis['intent'].value}")
        print(f"   Entities: {analysis['entities']}")
        print(f"   Tables: {analysis['tables']}")
        print(f"   Confidence: {analysis['confidence']:.2f}")
        
        # 3. Handle based on intent
        if analysis['intent'] == QueryIntent.CONVERSATIONAL:
            return self._handle_conversational(query, vector_results, start_time)
        
        elif analysis['intent'] == QueryIntent.PERMISSION:
            return self._handle_permission_query(query, vector_results, start_time)
        
        else:
            return self._handle_database_query(query, analysis, vector_results, start_time)
    
    def _handle_database_query(
        self,
        query: str,
        analysis: Dict,
        vector_results: List[Dict],
        start_time: float
    ) -> Dict:
        """Handle database queries"""
        
        print("\n💾 Step 3: SQL Generation")
        
        # Generate SQL
        sql = self.query_processor.generate_sql(query, analysis, vector_results)
        
        if not sql:
            print("   ❌ Could not generate SQL")
            return self._fallback_response(query, "Could not generate SQL", start_time)
        
        print(f"   Generated: {sql}")
        
        # Validate and fix
        is_valid, message, fixed_sql = self.query_processor.validate_and_fix_sql(sql)
        
        if fixed_sql:
            sql = fixed_sql
            print(f"   Fixed: {sql}")
        
        if not is_valid:
            print(f"   ❌ Invalid: {message}")
            return self._fallback_response(query, message, start_time)
        
        # Execute
        print("\n⚡ Step 4: Execute SQL")
        try:
            results = self.db.execute_query(sql)
            print(f"   Got {len(results)} results")
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            return self._fallback_response(query, str(e), start_time)
        
        # Generate response
        print("\n💬 Step 5: Generate Response")
        response = self._generate_response(query, results, vector_results, analysis, sql)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Complete in {elapsed:.2f}s")
        
        return {
            'query': query,
            'response': response['response'],
            'sql_executed': sql,
            'results_count': len(results),
            'sample_results': results[:10],
            'intent': analysis['intent'].value,
            'confidence': analysis['confidence'],
            'response_time': elapsed,
            'success': True
        }
    
    def _handle_permission_query(
        self,
        query: str,
        vector_results: List[Dict],
        start_time: float
    ) -> Dict:
        """Handle permission/role queries"""
        
        print("\n🔐 Handling Permission Query")
        
        # Build context from vector results
        contexts = []
        for result in vector_results[:5]:
            if result['metadata'].get('type') in ['role_permissions', 'role_summary', 'business_logic']:
                contexts.append(result['content'])
        
        # Generate response
        system_prompt = """You are a permissions expert. Answer using the role/permission data provided in context.

CRITICAL:
- List ACTUAL permissions from the context
- Do NOT make up permissions
- Be specific with permission names
- Count accurately
"""
        
        response = self.groq.generate_response(
            query=query,
            context=contexts,
            system_prompt=system_prompt
        )
        
        elapsed = time.time() - start_time
        
        return {
            'query': query,
            'response': response['response'],
            'intent': 'permission',
            'response_time': elapsed,
            'success': True
        }
    
    def _handle_conversational(
        self,
        query: str,
        vector_results: List[Dict],
        start_time: float
    ) -> Dict:
        """Handle conversational queries"""
        
        system_prompt = """You are a helpful LMS assistant. Be friendly and helpful.

You can help with:
- Counting records (students, teachers, etc.)
- Listing information
- Searching for specific records
- Understanding roles and permissions

Be conversational and suggest specific queries."""
        
        response = self.groq.generate_response(
            query=query,
            context=[],
            system_prompt=system_prompt
        )
        
        elapsed = time.time() - start_time
        
        return {
            'query': query,
            'response': response['response'],
            'intent': 'conversational',
            'response_time': elapsed,
            'success': True
        }
    
    def _generate_response(
        self,
        query: str,
        results: List[Dict],
        vector_results: List[Dict],
        analysis: Dict,
        sql: str
    ) -> Dict:
        """Generate natural language response"""
        
        # Build context
        contexts = []
        
        # Add results
        if results:
            if analysis['intent'] == QueryIntent.COUNT and 'count' in results[0]:
                contexts.append(f"Database query result: {results[0]['count']}")
            else:
                result_str = f"Database returned {len(results)} records:\n"
                for i, row in enumerate(results[:5], 1):
                    result_str += f"\n{i}. " + ", ".join([f"{k}: {v}" for k, v in list(row.items())[:5]])
                contexts.append(result_str)
        
        # Add vector context
        for result in vector_results[:3]:
            contexts.append(result['content'][:500])
        
        # Generate response
        system_prompt = f"""You are a helpful LMS assistant. Answer the query using the database results.

Query Intent: {analysis['intent'].value}
SQL Executed: {sql}

Be concise and accurate. Use the actual data provided."""
        
        return self.groq.generate_response(
            query=query,
            context=contexts,
            system_prompt=system_prompt
        )
    
    def _fallback_response(self, query: str, error: str, start_time: float) -> Dict:
        """Fallback response"""
        return {
            'query': query,
            'response': "I encountered an error processing your query. Please try rephrasing.",
            'error': error,
            'response_time': time.time() - start_time,
            'success': False
        }


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    rag = EnhancedRAGService()
    
    test_queries = [
        "How many students are there?",
        "List all teachers",
        "What permissions does Teacher have?",
        "Find students named John",
        "Hello, what can you help me with?"
    ]
    
    for query in test_queries:
        result = rag.process_query(query)
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"Response: {result['response']}")
        print(f"Success: {result['success']}")