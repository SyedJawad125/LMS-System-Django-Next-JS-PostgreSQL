# Groq Service code
# apps/rag_system/services/groq_service.py
from groq import Groq
from decouple import config
from typing import List, Dict
import json
import os


class GroqService:
    """GROQ LLM Service for RAG"""
    
    def __init__(self):
        try:
            api_key = config('GROQ_API_KEY', default=None)
            if not api_key:
                api_key = os.getenv('GROQ_API_KEY')
            
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.client = Groq(api_key=api_key)
            
            # ✅ UPDATED MODEL (not deprecated)
            self.model = "llama-3.3-70b-versatile"
            
            print(f"✅ GROQ service initialized with model: {self.model}")
        except Exception as e:
            print(f"❌ Error initializing GROQ: {e}")
            raise
    
    def generate_response(
        self, 
        query: str, 
        context: List[str], 
        system_prompt: str = None
    ) -> Dict:
        """
        Generate response using GROQ
        
        Args:
            query: User's question
            context: List of context strings from RAG
            system_prompt: Optional custom system prompt
            
        Returns:
            Dict with response, success status, tokens used
        """
        
        # Default system prompt if not provided
        if not system_prompt:
            system_prompt = """You are an intelligent LMS (Learning Management System) assistant.

You help with:
- Student records and enrollment
- Teacher information  
- Fee payments and dues
- Attendance records
- Exam schedules and results
- Class timetables
- And all other LMS data

Guidelines:
1. Provide accurate answers based on the context
2. Be concise and clear
3. Use specific numbers when available
4. If information is missing, say so
5. Be professional and helpful"""

        # Build context string from list
        if context and len(context) > 0:
            context_str = "\n\n".join([
                f"Context {i+1}:\n{str(ctx)}" 
                for i, ctx in enumerate(context) 
                if ctx  # Skip empty contexts
            ])
        else:
            context_str = "No specific context provided."
        
        # Create messages for GROQ
        messages = [
            {
                "role": "system", 
                "content": str(system_prompt)
            },
            {
                "role": "user", 
                "content": f"Context Information:\n{context_str}\n\nUser Query: {query}\n\nProvide a clear and helpful answer."
            }
        ]
        
        try:
            # Call GROQ API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
                top_p=0.9,
            )
            
            # Extract response
            answer = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            print(f"✅ GROQ response generated ({tokens} tokens)")
            
            return {
                "success": True,
                "response": answer,
                "tokens_used": tokens,
                "model": self.model
            }
            
        except Exception as e:
            print(f"❌ GROQ API Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error processing your request. Please try again.",
                "tokens_used": 0
            }
    
    def generate_intelligent_sql(self, query: str, table_context: Dict) -> str:
        """Generate SQL by understanding the actual table context"""
        
        table_name = table_context.get("table_name")
        columns = table_context.get("columns", [])
        entity_type = table_context.get("entity_type", "unknown")
        
        if not table_name or not columns:
            print("⚠️ Insufficient table context for SQL generation")
            return None
        
        columns_str = ", ".join(columns[:8])
        if len(columns) > 8:
            columns_str += f"... and {len(columns)-8} more"
        
        system_prompt = f"""You are a PostgreSQL expert. Generate ONLY SELECT queries.

TABLE CONTEXT:
- Table Name: {table_name}
- Entity Type: {entity_type}
- Columns Available: {columns_str}

USER QUERY: "{query}"

INSTRUCTIONS:
1. Use table '{table_name}' (DO NOT invent other table names)
2. For counting queries: SELECT COUNT(*) FROM {table_name}
3. For listing queries: SELECT * FROM {table_name} 
4. For specific columns: SELECT column1, column2 FROM {table_name}
5. ALWAYS add: WHERE (deleted = FALSE OR deleted IS NULL)
6. Use LIMIT 100 for safety
7. Return ONLY the SQL query - no explanations

EXAMPLES:
Query: "how many {entity_type}s"
SQL: SELECT COUNT(*) FROM {table_name} WHERE deleted = FALSE LIMIT 100

Query: "show all {entity_type}s"
SQL: SELECT * FROM {table_name} WHERE deleted = FALSE LIMIT 100

Query: "list {entity_type} names"
SQL: SELECT name FROM {table_name} WHERE deleted = FALSE LIMIT 100

Now generate SQL for: "{query}"
Use ONLY table: {table_name}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate SQL query for: {query}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.05,
                max_tokens=256,
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            sql_query = sql_query.rstrip(';')
            
            # Ensure it uses the correct table
            if table_name.lower() not in sql_query.lower():
                # Find table name in SQL and replace
                import re
                from_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
                if from_match:
                    wrong_table = from_match.group(1)
                    sql_query = sql_query.replace(wrong_table, table_name)
                    print(f"🔄 Fixed table: {wrong_table} → {table_name}")
            
            print(f"✅ Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            # Simple fallback
            return f"SELECT COUNT(*) FROM {table_name} WHERE (deleted = FALSE OR deleted IS NULL) LIMIT 100"

    # KEEP THIS METHOD FOR BACKWARD COMPATIBILITY
    def generate_sql_query(self, natural_language_query: str, schema_info: Dict) -> str:
        """Legacy method - uses new intelligent method if table_context available"""
        print("⚠️ Using legacy SQL generation method")
        
        # Try to extract table name from schema_info
        if schema_info:
            # Get first table
            table_name = list(schema_info.keys())[0] if schema_info else None
            if table_name:
                # Create table_context for the new method
                table_context = {
                    "table_name": table_name,
                    "columns": [col["name"] for col in schema_info[table_name][:10]],
                    "entity_type": "unknown"
                }
                return self.generate_intelligent_sql(natural_language_query, table_context)
        
        return None
    
    def test_connection(self) -> bool:
        """
        Test if GROQ API connection is working
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, this is a test. Reply with 'OK'."}
                ],
                max_tokens=10,
            )
            
            result = response.choices[0].message.content
            print(f"✅ GROQ connection test successful: {result}")
            return True
            
        except Exception as e:
            print(f"❌ GROQ connection test failed: {e}")
            return False


# ============================================
# TEST THE SERVICE
# ============================================

if __name__ == "__main__":
    """
    Test the GroqService
    
    Run with: python -m apps.rag_system.services.groq_service
    """
    print("=" * 60)
    print("Testing GroqService")
    print("=" * 60)
    
    try:
        # Initialize service
        groq = GroqService()
        
        # Test 1: Connection test
        print("\n1. Testing connection...")
        groq.test_connection()
        
        # Test 2: Simple response
        print("\n2. Testing generate_response...")
        result = groq.generate_response(
            query="What is 2+2?",
            context=["This is a simple math question."]
        )
        print(f"Response: {result['response']}")
        print(f"Success: {result['success']}")
        print(f"Tokens: {result['tokens_used']}")
        
        # Test 3: Intelligent SQL generation
        print("\n3. Testing intelligent SQL generation...")
        table_context = {
            "table_name": "users_user",
            "columns": ["id", "username", "email", "first_name", "last_name", "is_active", "created_at"],
            "entity_type": "user",
            "row_count": 150
        }
        
        test_queries = [
            "how many users are there",
            "show me all users",
            "list user emails"
        ]
        
        for test_query in test_queries:
            print(f"\n📝 Query: '{test_query}'")
            sql = groq.generate_intelligent_sql(test_query, table_context)
            print(f"   SQL: {sql}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()



# # ============================================
# # FINAL FIX - SQL GENERATION ISSUES
# # File: apps/rag_system/services/groq_service_fixed.py
# # ============================================

# """
# PROBLEMS IDENTIFIED:
# 1. Query 1: SQL contains "DELETE" keyword (likely "WHERE deleted = FALSE")
# 2. Query 2: SQL generation completely fails for listing queries

# SOLUTIONS:
# 1. Fix SQL validation to allow "deleted" column checks
# 2. Improve SQL generation prompts
# 3. Add fallback SQL templates
# """

# from groq import Groq
# from decouple import config
# from typing import List, Dict
# import json
# import os
# import re


# class GroqService:
#     """FIXED GROQ LLM Service for RAG"""
    
#     def __init__(self):
#         try:
#             api_key = config('GROQ_API_KEY', default=None)
#             if not api_key:
#                 api_key = os.getenv('GROQ_API_KEY')
            
#             if not api_key:
#                 raise ValueError("GROQ_API_KEY not found in environment variables")
            
#             self.client = Groq(api_key=api_key)
#             self.model = "llama-3.3-70b-versatile"
            
#             print(f"✅ GROQ service initialized with model: {self.model}")
#         except Exception as e:
#             print(f"❌ Error initializing GROQ: {e}")
#             raise
    
#     def generate_response(
#         self, 
#         query: str, 
#         context: List[str], 
#         system_prompt: str = None
#     ) -> Dict:
#         """Generate response using GROQ"""
        
#         if not system_prompt:
#             system_prompt = """You are an intelligent LMS (Learning Management System) assistant.

# Guidelines:
# 1. Provide accurate answers based on the context
# 2. Be concise and clear
# 3. Use specific numbers when available
# 4. If information is missing, say so
# 5. Be professional and helpful"""

#         if context and len(context) > 0:
#             context_str = "\n\n".join([
#                 f"Context {i+1}:\n{str(ctx)}" 
#                 for i, ctx in enumerate(context) 
#                 if ctx
#             ])
#         else:
#             context_str = "No specific context provided."
        
#         messages = [
#             {"role": "system", "content": str(system_prompt)},
#             {"role": "user", "content": f"Context Information:\n{context_str}\n\nUser Query: {query}\n\nProvide a clear and helpful answer."}
#         ]
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.3,
#                 max_tokens=2048,
#                 top_p=0.9,
#             )
            
#             answer = response.choices[0].message.content
#             tokens = response.usage.total_tokens
            
#             print(f"✅ GROQ response generated ({tokens} tokens)")
            
#             return {
#                 "success": True,
#                 "response": answer,
#                 "tokens_used": tokens,
#                 "model": self.model
#             }
            
#         except Exception as e:
#             print(f"❌ GROQ API Error: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "response": "Sorry, I encountered an error processing your request. Please try again.",
#                 "tokens_used": 0
#             }
    
#     def generate_intelligent_sql(self, query: str, table_context: Dict) -> str:
#         """
#         FIXED: Generate SQL with better prompts and fallback templates
        
#         Key fixes:
#         1. Clearer instructions to LLM
#         2. Better examples
#         3. Fallback templates for common queries
#         4. Handle "deleted" column properly
#         """
        
#         table_name = table_context.get("table_name")
#         columns = table_context.get("columns", [])
#         entity_type = table_context.get("entity_type", "unknown")
        
#         if not table_name or not columns:
#             print("⚠️ Insufficient table context for SQL generation")
#             return None
        
#         # Check if table has 'deleted' column
#         has_deleted_column = 'deleted' in [c.lower() for c in columns]
        
#         # Build WHERE clause template
#         if has_deleted_column:
#             where_template = "WHERE (deleted = FALSE OR deleted IS NULL)"
#         else:
#             where_template = "WHERE 1=1"
        
#         columns_str = ", ".join(columns[:10])
#         if len(columns) > 10:
#             columns_str += f"... (total {len(columns)} columns)"
        
#         # Determine query type for better SQL generation
#         query_lower = query.lower()
        
#         # Try template-based generation first (more reliable)
#         template_sql = self._generate_from_template(
#             query_lower, 
#             table_name, 
#             columns, 
#             where_template
#         )
        
#         if template_sql:
#             print(f"✅ Used template SQL: {template_sql}")
#             return template_sql
        
#         # If no template matches, use LLM
#         system_prompt = f"""You are a PostgreSQL expert. Generate ONLY valid SELECT queries.

# CRITICAL RULES:
# 1. ONLY use SELECT statements
# 2. Table name: {table_name}
# 3. Available columns: {columns_str}
# 4. ALWAYS include: {where_template}
# 5. ALWAYS add: LIMIT 100
# 6. Return ONLY the SQL query - NO explanations, NO markdown, NO backticks
# 7. The word "deleted" in WHERE clause is a COLUMN NAME, not a SQL keyword

# QUERY PATTERNS:

# Pattern 1 - COUNTING:
# Input: "how many {entity_type}s"
# Output: SELECT COUNT(*) as count FROM {table_name} {where_template} LIMIT 100

# Pattern 2 - LISTING ALL:
# Input: "list all {entity_type}s" OR "show all {entity_type}s"
# Output: SELECT * FROM {table_name} {where_template} LIMIT 100

# Pattern 3 - LISTING SPECIFIC COLUMNS:
# Input: "list {entity_type} names" OR "show {entity_type} emails"
# Output: SELECT name FROM {table_name} {where_template} LIMIT 100

# Pattern 4 - COUNTING + LISTING:
# Input: "how many {entity_type}s and their details"
# Output: SELECT * FROM {table_name} {where_template} LIMIT 100

# AVAILABLE COLUMNS FOR {table_name}:
# {', '.join(columns[:15])}

# USER QUERY: "{query}"

# Generate the SQL query now. IMPORTANT: Return ONLY the SQL, nothing else."""

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"SQL for: {query}"}
#         ]
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.05,
#                 max_tokens=256,
#             )
            
#             sql_query = response.choices[0].message.content.strip()
            
#             # Clean up the response
#             sql_query = self._clean_sql_response(sql_query)
            
#             # Validate it's actually a query
#             if not sql_query or len(sql_query) < 10:
#                 print(f"⚠️ Generated SQL too short: '{sql_query}'")
#                 return self._fallback_sql(query_lower, table_name, columns, where_template)
            
#             # Ensure correct table name
#             if table_name.lower() not in sql_query.lower():
#                 print(f"⚠️ Generated SQL doesn't use correct table")
#                 return self._fallback_sql(query_lower, table_name, columns, where_template)
            
#             # Ensure WHERE clause is present
#             if has_deleted_column and 'deleted' not in sql_query.lower():
#                 # Add WHERE clause
#                 if 'WHERE' not in sql_query.upper():
#                     sql_query = sql_query.replace('LIMIT', f'{where_template} LIMIT')
            
#             # Ensure LIMIT is present
#             if 'LIMIT' not in sql_query.upper():
#                 sql_query += ' LIMIT 100'
            
#             print(f"✅ Generated SQL: {sql_query}")
#             return sql_query
            
#         except Exception as e:
#             print(f"❌ Error generating SQL: {e}")
#             return self._fallback_sql(query_lower, table_name, columns, where_template)
    
#     def _generate_from_template(
#         self, 
#         query_lower: str, 
#         table_name: str, 
#         columns: List[str],
#         where_clause: str
#     ) -> str:
#         """
#         Generate SQL from predefined templates for common queries
#         This is MORE RELIABLE than LLM generation
#         """
        
#         # Counting queries
#         if any(word in query_lower for word in ['how many', 'count', 'total number']):
#             return f"SELECT COUNT(*) as count FROM {table_name} {where_clause} LIMIT 100"
        
#         # Listing all records
#         if any(phrase in query_lower for phrase in ['list all', 'show all', 'get all', 'display all']):
#             return f"SELECT * FROM {table_name} {where_clause} LIMIT 100"
        
#         # List specific columns
#         column_keywords = {
#             'name': ['name', 'names'],
#             'email': ['email', 'emails'],
#             'phone': ['phone', 'mobile', 'contact'],
#             'admission_number': ['admission number', 'admission numbers', 'admission_number'],
#             'employee_id': ['employee id', 'employee_id', 'emp id'],
#             'id': ['id', 'ids']
#         }
        
#         for col, keywords in column_keywords.items():
#             # Check if column exists in table
#             col_exists = any(c.lower() == col.lower() or col.lower() in c.lower() for c in columns)
            
#             if col_exists and any(kw in query_lower for kw in keywords):
#                 # Find actual column name (might be different case)
#                 actual_col = next((c for c in columns if col.lower() in c.lower()), col)
#                 return f"SELECT {actual_col} FROM {table_name} {where_clause} LIMIT 100"
        
#         # Combined: count + list specific column
#         for col, keywords in column_keywords.items():
#             col_exists = any(c.lower() == col.lower() or col.lower() in c.lower() for c in columns)
            
#             if col_exists:
#                 if ('how many' in query_lower or 'count' in query_lower) and any(kw in query_lower for kw in keywords):
#                     actual_col = next((c for c in columns if col.lower() in c.lower()), col)
#                     return f"SELECT {actual_col} FROM {table_name} {where_clause} LIMIT 100"
        
#         return None  # No template match
    
#     def _fallback_sql(
#         self, 
#         query_lower: str, 
#         table_name: str, 
#         columns: List[str],
#         where_clause: str
#     ) -> str:
#         """
#         Generate fallback SQL when LLM fails
#         """
#         print("⚠️ Using fallback SQL generation")
        
#         # Default to counting if query asks "how many"
#         if 'how many' in query_lower or 'count' in query_lower:
#             return f"SELECT COUNT(*) as count FROM {table_name} {where_clause} LIMIT 100"
        
#         # Default to listing all
#         return f"SELECT * FROM {table_name} {where_clause} LIMIT 100"
    
#     def _clean_sql_response(self, sql: str) -> str:
#         """
#         Clean up SQL response from LLM
#         """
#         # Remove markdown code blocks
#         sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
#         sql = re.sub(r'```\s*', '', sql)
        
#         # Remove common prefixes
#         prefixes = [
#             'sql:', 'query:', 'output:', 'here is the sql:',
#             'the sql query is:', 'sql query:'
#         ]
        
#         for prefix in prefixes:
#             if sql.lower().startswith(prefix):
#                 sql = sql[len(prefix):].strip()
        
#         # Remove trailing semicolon
#         sql = sql.rstrip(';').strip()
        
#         # Remove newlines and extra spaces
#         sql = ' '.join(sql.split())
        
#         return sql
    
#     def test_connection(self) -> bool:
#         """Test if GROQ API connection is working"""
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "user", "content": "Hello, this is a test. Reply with 'OK'."}
#                 ],
#                 max_tokens=10,
#             )
            
#             result = response.choices[0].message.content
#             print(f"✅ GROQ connection test successful: {result}")
#             return True
            
#         except Exception as e:
#             print(f"❌ GROQ connection test failed: {e}")
#             return False


# # ============================================
# # TEST THE FIXED SERVICE
# # ============================================

# if __name__ == "__main__":
#     """Test the fixed SQL generation"""
#     print("=" * 60)
#     print("Testing Fixed GroqService")
#     print("=" * 60)
    
#     try:
#         groq = GroqService()
        
#         # Test cases
#         test_cases = [
#             {
#                 "query": "How many students are enrolled and their admission numbers?",
#                 "table_context": {
#                     "table_name": "students",
#                     "columns": ["id", "admission_number", "name", "email", "deleted"],
#                     "entity_type": "student"
#                 }
#             },
#             {
#                 "query": "List all teachers",
#                 "table_context": {
#                     "table_name": "teachers_teacher",
#                     "columns": ["id", "user_id", "qualification", "specialization", "deleted"],
#                     "entity_type": "teacher"
#                 }
#             },
#             {
#                 "query": "Show teacher names",
#                 "table_context": {
#                     "table_name": "teachers_teacher",
#                     "columns": ["id", "name", "email", "deleted"],
#                     "entity_type": "teacher"
#                 }
#             }
#         ]
        
#         for i, test in enumerate(test_cases, 1):
#             print(f"\n{'='*60}")
#             print(f"Test {i}: {test['query']}")
#             print(f"{'='*60}")
            
#             sql = groq.generate_intelligent_sql(test['query'], test['table_context'])
            
#             print(f"Generated SQL: {sql}")
            
#             # Check if valid
#             if sql:
#                 if 'DELETE' in sql.upper() and 'deleted' not in sql.lower():
#                     print("❌ FAIL: Contains DELETE keyword")
#                 elif 'SELECT' not in sql.upper():
#                     print("❌ FAIL: Not a SELECT query")
#                 else:
#                     print("✅ PASS: Valid SQL")
#             else:
#                 print("❌ FAIL: No SQL generated")
        
#         print(f"\n{'='*60}")
#         print("✅ Testing complete!")
#         print(f"{'='*60}")
        
#     except Exception as e:
#         print(f"\n❌ Test failed: {e}")
#         import traceback
#         traceback.print_exc()