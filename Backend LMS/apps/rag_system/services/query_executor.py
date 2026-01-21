# # ============================================
# # QUERY EXECUTOR - Execute Real Database Queries
# # File: apps/rag_system/services/query_executor.py
# # ============================================

# from typing import Dict, List, Optional
# from .database_connector import DatabaseConnector
# from .groq_service import GroqService


# class QueryExecutor:
#     """
#     Execute database queries and return structured results
    
#     This is the CRITICAL missing piece - actually querying the database
#     instead of just reading schema metadata.
#     """
    
#     def __init__(self):
#         self.db_connector = DatabaseConnector()
#         self.groq_service = GroqService()
#         self.max_results = 100  # Safety limit
    
#     def execute_user_query(
#         self, 
#         query: str, 
#         table_context: Dict
#     ) -> Dict:
#         """
#         Execute user's natural language query against database
        
#         Args:
#             query: Natural language query from user
#             table_context: {
#                 "table_name": "students",
#                 "columns": ["id", "name", ...],
#                 "entity_type": "student"
#             }
        
#         Returns:
#             {
#                 "success": True/False,
#                 "sql": "SELECT ...",
#                 "results": [...],
#                 "row_count": 123,
#                 "error": None
#             }
#         """
#         try:
#             # Step 1: Generate SQL from natural language
#             print(f"🔍 Generating SQL for: {query}")
#             sql = self.groq_service.generate_intelligent_sql(query, table_context)
            
#             if not sql:
#                 return self._no_sql_generated(query)
            
#             print(f"✅ Generated SQL: {sql}")
            
#             # Step 2: Validate SQL for safety
#             is_valid, validation_error = self._validate_sql(sql)
#             if not is_valid:
#                 print(f"❌ SQL validation failed: {validation_error}")
#                 return {
#                     "success": False,
#                     "sql": sql,
#                     "results": [],
#                     "row_count": 0,
#                     "error": f"Invalid SQL: {validation_error}"
#                 }
            
#             # Step 3: Execute SQL
#             print(f"📊 Executing query...")
#             results = self.db_connector.execute_query(sql)
            
#             # Limit results for safety
#             if len(results) > self.max_results:
#                 results = results[:self.max_results]
#                 print(f"⚠️ Limited results to {self.max_results}")
            
#             print(f"✅ Got {len(results)} results")
            
#             return {
#                 "success": True,
#                 "sql": sql,
#                 "results": results,
#                 "row_count": len(results),
#                 "error": None
#             }
            
#         except Exception as e:
#             print(f"❌ Query execution error: {e}")
#             import traceback
#             traceback.print_exc()
            
#             return {
#                 "success": False,
#                 "sql": sql if 'sql' in locals() else None,
#                 "results": [],
#                 "row_count": 0,
#                 "error": str(e)
#             }
    
#     def _validate_sql(self, sql: str) -> tuple:
#         """
#         Validate SQL for safety
        
#         Returns:
#             (is_valid: bool, error_message: str)
#         """
#         if not sql or len(sql.strip()) == 0:
#             return False, "Empty SQL query"
        
#         sql_upper = sql.upper().strip()
        
#         # Must start with SELECT
#         if not sql_upper.startswith('SELECT'):
#             return False, "Only SELECT queries allowed"
        
#         # Check for dangerous keywords
#         dangerous_keywords = [
#             'DROP', 'DELETE', 'UPDATE', 'INSERT',
#             'ALTER', 'TRUNCATE', 'CREATE', 'GRANT',
#             'REVOKE', 'EXEC', 'EXECUTE'
#         ]
        
#         for keyword in dangerous_keywords:
#             if keyword in sql_upper:
#                 return False, f"Forbidden keyword: {keyword}"
        
#         # Check for multiple statements
#         if sql.count(';') > 1:
#             return False, "Multiple statements not allowed"
        
#         # Check for SQL injection patterns
#         suspicious_patterns = ['--', '/*', '*/', 'xp_', 'sp_']
#         for pattern in suspicious_patterns:
#             if pattern in sql:
#                 return False, f"Suspicious pattern detected: {pattern}"
        
#         return True, ""
    
#     def _no_sql_generated(self, query: str) -> Dict:
#         """Handle case where SQL generation failed"""
#         return {
#             "success": False,
#             "sql": None,
#             "results": [],
#             "row_count": 0,
#             "error": "Could not generate SQL query from natural language"
#         }
    
#     def format_results_for_llm(
#         self, 
#         results: List[Dict], 
#         query: str
#     ) -> str:
#         """
#         Format query results for LLM context
        
#         Creates a human-readable representation of database results
#         that the LLM can use to generate responses.
        
#         Args:
#             results: List of result dictionaries from database
#             query: Original query (used for context-aware formatting)
        
#         Returns:
#             Formatted string of results
#         """
#         if not results:
#             return "No results found in database."
        
#         # Limit results to prevent context overflow
#         limited_results = results[:50]
#         query_lower = query.lower()
        
#         # For counting queries, special format
#         if any(word in query_lower for word in ['count', 'how many', 'number of', 'total']):
#             if len(results) == 1 and 'count' in results[0]:
#                 # Direct count query result
#                 count_value = results[0]['count']
#                 return f"Database query returned count: {count_value}"
#             else:
#                 # List query where we want to count items
#                 return f"Database query returned {len(results)} records."
        
#         # For list queries, format as readable table
#         formatted = ["=== Database Query Results ===\n"]
        
#         # Get column names from first result
#         if limited_results:
#             columns = list(limited_results[0].keys())
            
#             # Format header
#             formatted.append(f"Columns: {', '.join(columns)}\n")
            
#             # Format each row
#             for i, row in enumerate(limited_results, 1):
#                 row_parts = []
#                 for col in columns:
#                     value = row.get(col, 'NULL')
#                     # Format dates, booleans, etc.
#                     if isinstance(value, bool):
#                         value = 'Yes' if value else 'No'
#                     row_parts.append(f"{col}: {value}")
                
#                 formatted.append(f"{i}. {' | '.join(row_parts)}")
        
#         if len(results) > 50:
#             formatted.append(f"\n... and {len(results) - 50} more records (showing first 50)")
        
#         formatted.append(f"\nTotal records: {len(results)}")
        
#         return "\n".join(formatted)
    
#     def format_results_for_user(
#         self,
#         results: List[Dict],
#         query: str
#     ) -> Dict:
#         """
#         Format results for API response (user-facing)
        
#         Returns:
#             {
#                 "summary": "Found 6 students",
#                 "data": [...],
#                 "formatted_text": "1. John Doe...",
#                 "count": 6
#             }
#         """
#         if not results:
#             return {
#                 "summary": "No results found",
#                 "data": [],
#                 "formatted_text": "No records match your query.",
#                 "count": 0
#             }
        
#         query_lower = query.lower()
        
#         # Check if counting query
#         is_count_query = any(
#             word in query_lower 
#             for word in ['count', 'how many', 'number of', 'total']
#         )
        
#         if is_count_query and len(results) == 1 and 'count' in results[0]:
#             count = results[0]['count']
#             return {
#                 "summary": f"Count: {count}",
#                 "data": results,
#                 "formatted_text": f"There are {count} records.",
#                 "count": count
#             }
        
#         # Format list results
#         formatted_lines = []
#         for i, row in enumerate(results[:20], 1):  # Limit display to 20
#             # Create readable line from row
#             row_str = f"{i}. " + " | ".join([
#                 f"{k}: {v}" for k, v in row.items()
#             ])
#             formatted_lines.append(row_str)
        
#         if len(results) > 20:
#             formatted_lines.append(f"\n... and {len(results) - 20} more records")
        
#         return {
#             "summary": f"Found {len(results)} records",
#             "data": results[:20],  # Limit data payload
#             "formatted_text": "\n".join(formatted_lines),
#             "count": len(results)
#         }


# # ============================================
# # TESTING
# # ============================================

# if __name__ == "__main__":
#     """Test the QueryExecutor"""
#     print("="*60)
#     print("Testing QueryExecutor")
#     print("="*60)
    
#     try:
#         executor = QueryExecutor()
        
#         # Test query
#         test_query = "how many students are enrolled"
#         table_context = {
#             "table_name": "students",
#             "columns": ["id", "admission_number", "name", "email"],
#             "entity_type": "student"
#         }
        
#         print(f"\n📝 Test Query: '{test_query}'")
#         result = executor.execute_user_query(test_query, table_context)
        
#         print(f"\nResult:")
#         print(f"  Success: {result['success']}")
#         print(f"  SQL: {result['sql']}")
#         print(f"  Row Count: {result['row_count']}")
#         if result['results']:
#             print(f"  First Result: {result['results'][0]}")
        
#         # Test formatting
#         if result['success'] and result['results']:
#             formatted = executor.format_results_for_llm(
#                 result['results'],
#                 test_query
#             )
#             print(f"\nFormatted for LLM:")
#             print(formatted[:500])
        
#         print("\n" + "="*60)
#         print("✅ Test complete!")
#         print("="*60)
        
#     except Exception as e:
#         print(f"❌ Test failed: {e}")
#         import traceback
#         traceback.print_exc()





# ============================================
# FINAL FIXED QUERY EXECUTOR
# File: apps/rag_system/services/query_executor.py
# ============================================

from typing import Dict, List, Optional
from .database_connector import DatabaseConnector
from .groq_service import GroqService


class QueryExecutor:
    """Execute database queries - FIXED to not block 'deleted' column"""
    
    def __init__(self):
        self.db_connector = DatabaseConnector()
        self.groq_service = GroqService()
        self.max_results = 100
    
    def execute_user_query(
        self, 
        query: str, 
        table_context: Dict
    ) -> Dict:
        """Execute user's query against database"""
        try:
            # Generate SQL
            print(f"🔍 Generating SQL for: {query}")
            sql = self.groq_service.generate_intelligent_sql(query, table_context)
            
            if not sql:
                return self._no_sql_generated(query)
            
            print(f"✅ Generated SQL: {sql}")
            
            # Validate SQL
            is_valid, validation_error = self._validate_sql(sql)
            if not is_valid:
                print(f"❌ SQL validation failed: {validation_error}")
                return {
                    "success": False,
                    "sql": sql,
                    "results": [],
                    "row_count": 0,
                    "error": f"Invalid SQL: {validation_error}"
                }
            
            # Execute SQL
            print(f"📊 Executing query...")
            results = self.db_connector.execute_query(sql)
            
            # Limit results
            if len(results) > self.max_results:
                results = results[:self.max_results]
                print(f"⚠️ Limited to {self.max_results}")
            
            print(f"✅ Got {len(results)} results")
            
            return {
                "success": True,
                "sql": sql,
                "results": results,
                "row_count": len(results),
                "error": None
            }
            
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "sql": sql if 'sql' in locals() else None,
                "results": [],
                "row_count": 0,
                "error": str(e)
            }
    
    def _validate_sql(self, sql: str) -> tuple:
        """
        Validate SQL - FIXED to not block 'deleted' column
        
        We need to block:
        - DELETE FROM table
        - UPDATE table SET
        - DROP TABLE
        
        We should NOT block:
        - WHERE deleted = false
        - SELECT deleted FROM table
        """
        if not sql or len(sql.strip()) == 0:
            return False, "Empty SQL query"
        
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries allowed"
        
        # Check for DANGEROUS patterns (commands, not column names)
        # These patterns check for DELETE/UPDATE/DROP as COMMANDS, not column names
        import re
        
        # Block: DELETE FROM (command)
        if re.search(r'\bDELETE\s+FROM\b', sql_upper):
            return False, "Forbidden: DELETE FROM command"
        
        # Block: UPDATE table SET (command)
        if re.search(r'\bUPDATE\s+\w+\s+SET\b', sql_upper):
            return False, "Forbidden: UPDATE SET command"
        
        # Block: DROP TABLE/DATABASE (command)
        if re.search(r'\bDROP\s+(TABLE|DATABASE)\b', sql_upper):
            return False, "Forbidden: DROP command"
        
        # Block: INSERT INTO (command)
        if re.search(r'\bINSERT\s+INTO\b', sql_upper):
            return False, "Forbidden: INSERT command"
        
        # Block: TRUNCATE TABLE (command)
        if re.search(r'\bTRUNCATE\s+TABLE\b', sql_upper):
            return False, "Forbidden: TRUNCATE command"
        
        # Block: ALTER TABLE (command)
        if re.search(r'\bALTER\s+TABLE\b', sql_upper):
            return False, "Forbidden: ALTER command"
        
        # Block multiple statements
        if sql.count(';') > 1:
            return False, "Multiple statements not allowed"
        
        # Block SQL injection patterns
        suspicious_patterns = ['--', '/*', '*/', 'xp_', 'sp_']
        for pattern in suspicious_patterns:
            if pattern in sql:
                return False, f"Suspicious pattern: {pattern}"
        
        return True, ""
    
    def _no_sql_generated(self, query: str) -> Dict:
        """Handle case where SQL generation failed"""
        return {
            "success": False,
            "sql": None,
            "results": [],
            "row_count": 0,
            "error": "Could not generate SQL query"
        }
    
    def format_results_for_llm(
        self, 
        results: List[Dict], 
        query: str
    ) -> str:
        """Format results for LLM context"""
        if not results:
            return "No results found in database."
        
        limited_results = results[:50]
        query_lower = query.lower()
        
        # For counting queries
        if any(word in query_lower for word in ['count', 'how many', 'number of', 'total']):
            if len(results) == 1 and 'count' in results[0]:
                count_value = results[0]['count']
                return f"Database query returned count: {count_value}"
            else:
                return f"Database query returned {len(results)} records."
        
        # For list queries
        formatted = ["=== Database Query Results ===\n"]
        
        if limited_results:
            columns = list(limited_results[0].keys())
            formatted.append(f"Columns: {', '.join(columns)}\n")
            
            for i, row in enumerate(limited_results, 1):
                row_parts = []
                for col in columns:
                    value = row.get(col, 'NULL')
                    if isinstance(value, bool):
                        value = 'Yes' if value else 'No'
                    row_parts.append(f"{col}: {value}")
                
                formatted.append(f"{i}. {' | '.join(row_parts)}")
        
        if len(results) > 50:
            formatted.append(f"\n... and {len(results) - 50} more records")
        
        formatted.append(f"\nTotal records: {len(results)}")
        
        return "\n".join(formatted)
    
    def format_results_for_user(
        self,
        results: List[Dict],
        query: str
    ) -> Dict:
        """Format results for API response"""
        if not results:
            return {
                "summary": "No results found",
                "data": [],
                "formatted_text": "No records match your query.",
                "count": 0
            }
        
        query_lower = query.lower()
        
        is_count_query = any(
            word in query_lower 
            for word in ['count', 'how many', 'number of', 'total']
        )
        
        if is_count_query and len(results) == 1 and 'count' in results[0]:
            count = results[0]['count']
            return {
                "summary": f"Count: {count}",
                "data": results,
                "formatted_text": f"There are {count} records.",
                "count": count
            }
        
        # Format list results
        formatted_lines = []
        for i, row in enumerate(results[:20], 1):
            row_str = f"{i}. " + " | ".join([
                f"{k}: {v}" for k, v in row.items()
            ])
            formatted_lines.append(row_str)
        
        if len(results) > 20:
            formatted_lines.append(f"\n... and {len(results) - 20} more records")
        
        return {
            "summary": f"Found {len(results)} records",
            "data": results[:20],
            "formatted_text": "\n".join(formatted_lines),
            "count": len(results)
        }


# TESTING
if __name__ == "__main__":
    print("="*60)
    print("Testing FINAL FIXED QueryExecutor")
    print("="*60)
    
    try:
        executor = QueryExecutor()
        
        # Test SQL validation
        test_sqls = [
            ("SELECT * FROM routes WHERE deleted = false LIMIT 100", True),
            ("SELECT deleted FROM routes", True),
            ("DELETE FROM routes WHERE id = 1", False),
            ("UPDATE routes SET name = 'x'", False),
            ("SELECT * FROM routes; DROP TABLE routes;", False),
        ]
        
        print("\nTesting SQL Validation:")
        for sql, should_pass in test_sqls:
            is_valid, error = executor._validate_sql(sql)
            status = "✅ PASS" if is_valid == should_pass else "❌ FAIL"
            print(f"{status}: {sql[:50]}...")
            if not is_valid:
                print(f"        Reason: {error}")
        
        print("\n" + "="*60)
        print("✅ Testing complete")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()




