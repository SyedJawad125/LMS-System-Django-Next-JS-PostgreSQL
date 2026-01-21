# # ============================================
# # FIXED GROQ SERVICE - Prevents Invalid SQL
# # File: apps/rag_system/services/groq_service.py
# # ============================================

# from groq import Groq
# from decouple import config
# from typing import List, Dict
# import json
# import os
# import re


# class GroqService:
#     """GROQ LLM Service for RAG - FIXED VERSION"""
    
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

# You help with:
# - Student records and enrollment
# - Teacher information  
# - Fee payments and dues
# - Attendance records
# - Exam schedules and results
# - Class timetables
# - And all other LMS data

# Guidelines:
# 1. Provide accurate answers based on the context
# 2. Be concise and clear
# 3. Use specific numbers when available
# 4. If information is missing, say so
# 5. Be professional and helpful"""

#         # Build context string from list
#         if context and len(context) > 0:
#             context_str = "\n\n".join([
#                 f"Context {i+1}:\n{str(ctx)}" 
#                 for i, ctx in enumerate(context) 
#                 if ctx
#             ])
#         else:
#             context_str = "No specific context provided."
        
#         messages = [
#             {
#                 "role": "system", 
#                 "content": str(system_prompt)
#             },
#             {
#                 "role": "user", 
#                 "content": f"Context Information:\n{context_str}\n\nUser Query: {query}\n\nProvide a clear and helpful answer."
#             }
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
#         Generate SQL with STRICT safety checks
        
#         CRITICAL FIX: Prevents generating queries with DELETE, UPDATE, etc.
#         """
        
#         table_name = table_context.get("table_name")
#         columns = table_context.get("columns", [])
#         entity_type = table_context.get("entity_type", "unknown")
#         has_deleted_field = table_context.get("has_deleted_field", True)
        
#         if not table_name or not columns:
#             print("⚠️ Insufficient table context for SQL generation")
#             return None
        
#         # ============================================================
#         # SAFETY CHECK: Detect dangerous keywords in query
#         # ============================================================
#         query_upper = query.upper()
#         dangerous_keywords = ['DELETE', 'UPDATE', 'INSERT', 'DROP', 'ALTER', 'TRUNCATE']
        
#         for keyword in dangerous_keywords:
#             if keyword in query_upper:
#                 print(f"⚠️ WARNING: Query contains dangerous keyword '{keyword}'")
#                 print(f"   Converting to safe SELECT query")
#                 # Override query to be safe
#                 query = f"show all {entity_type}s"
        
#         # ============================================================
#         # Build safe column list
#         # ============================================================
#         columns_str = ", ".join(columns[:8])
#         if len(columns) > 8:
#             columns_str += f"... and {len(columns)-8} more"
        
#         # Build WHERE clause
#         where_clause = ""
#         if has_deleted_field:
#             where_clause = "WHERE (deleted = FALSE OR deleted IS NULL)"
        
#         # ============================================================
#         # ENHANCED SYSTEM PROMPT - Explicitly forbids dangerous SQL
#         # ============================================================
#         system_prompt = f"""You are a PostgreSQL expert. Generate ONLY safe SELECT queries.

# 🔴 CRITICAL RULES - NEVER VIOLATE:
# 1. ONLY generate SELECT statements
# 2. NEVER use: DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE, GRANT, REVOKE
# 3. NEVER generate queries that modify data
# 4. ALWAYS use the table name provided: {table_name}
# 5. ALWAYS add WHERE clause for deleted records if applicable

# TABLE CONTEXT:
# - Table Name: {table_name}
# - Entity Type: {entity_type}
# - Columns Available: {columns_str}
# - Has 'deleted' field: {has_deleted_field}

# USER QUERY: "{query}"

# QUERY TYPE DETECTION:
# - "how many" / "count" / "total" → SELECT COUNT(*) FROM {table_name}
# - "show" / "list" / "display" → SELECT * FROM {table_name}
# - "find" / "search" → SELECT * FROM {table_name} WHERE [condition]

# INSTRUCTIONS:
# 1. Detect query type (counting, listing, filtering)
# 2. Use ONLY SELECT statements
# 3. Use table '{table_name}' (DO NOT invent other table names)
# 4. Add WHERE clause: {where_clause if has_deleted_field else '(no WHERE needed)'}
# 5. Add LIMIT 100 for safety
# 6. Return ONLY the SQL query - no explanations, no markdown

# EXAMPLES:

# Query: "how many {entity_type}s"
# SQL: SELECT COUNT(*) as count FROM {table_name} {where_clause} LIMIT 100

# Query: "show all {entity_type}s"
# SQL: SELECT * FROM {table_name} {where_clause} LIMIT 100

# Query: "list {entity_type} names"
# SQL: SELECT id, name FROM {table_name} {where_clause} LIMIT 100

# Query: "{entity_type}s with experience > 5"
# SQL: SELECT * FROM {table_name} WHERE experience_years > 5 AND (deleted = FALSE OR deleted IS NULL) LIMIT 100

# Now generate SQL for: "{query}"
# Table: {table_name}
# Remember: ONLY SELECT queries allowed!"""

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"Generate safe SELECT query for: {query}"}
#         ]
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.05,  # Very low temperature for consistent SQL
#                 max_tokens=256,
#             )
            
#             sql_query = response.choices[0].message.content.strip()
            
#             # ============================================================
#             # CLEAN UP SQL
#             # ============================================================
#             # Remove markdown code blocks
#             sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
#             # Remove any explanatory text before/after SQL
#             lines = sql_query.split('\n')
#             sql_lines = []
#             for line in lines:
#                 line = line.strip()
#                 if line and (line.upper().startswith('SELECT') or 
#                            'FROM' in line.upper() or 
#                            'WHERE' in line.upper() or
#                            'LIMIT' in line.upper() or
#                            'ORDER BY' in line.upper()):
#                     sql_lines.append(line)
            
#             if sql_lines:
#                 sql_query = ' '.join(sql_lines)
            
#             # Remove trailing semicolon
#             sql_query = sql_query.rstrip(';').strip()
            
#             # ============================================================
#             # SAFETY VALIDATION
#             # ============================================================
#             sql_upper = sql_query.upper()
            
#             # Check 1: Must start with SELECT
#             if not sql_upper.startswith('SELECT'):
#                 print(f"⚠️ Generated SQL doesn't start with SELECT, fixing...")
#                 sql_query = f"SELECT * FROM {table_name} {where_clause} LIMIT 100"
            
#             # Check 2: No dangerous keywords
#             for keyword in dangerous_keywords:
#                 if keyword in sql_upper:
#                     print(f"❌ CRITICAL: Generated SQL contains '{keyword}', using safe fallback")
#                     # Use safe fallback
#                     if 'count' in query.lower() or 'how many' in query.lower():
#                         sql_query = f"SELECT COUNT(*) as count FROM {table_name} {where_clause}"
#                     else:
#                         sql_query = f"SELECT * FROM {table_name} {where_clause} LIMIT 100"
#                     break
            
#             # Check 3: Ensure correct table name is used
#             if table_name.lower() not in sql_query.lower():
#                 print(f"⚠️ SQL doesn't use correct table, fixing...")
#                 # Try to replace FROM clause
#                 import re
#                 from_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
#                 if from_match:
#                     wrong_table = from_match.group(1)
#                     sql_query = sql_query.replace(wrong_table, table_name)
#                     print(f"🔄 Fixed table: {wrong_table} → {table_name}")
            
#             # Check 4: Ensure deleted filter exists if needed
#             if has_deleted_field and 'deleted' not in sql_query.lower():
#                 print(f"⚠️ Adding deleted filter...")
#                 if 'WHERE' in sql_upper:
#                     # Add to existing WHERE
#                     sql_query = sql_query.replace('WHERE', f'WHERE (deleted = FALSE OR deleted IS NULL) AND', 1)
#                 else:
#                     # Add new WHERE before LIMIT
#                     if 'LIMIT' in sql_upper:
#                         sql_query = sql_query.replace('LIMIT', f'{where_clause} LIMIT', 1)
#                     else:
#                         sql_query = f"{sql_query} {where_clause}"
            
#             # Check 5: Ensure LIMIT exists
#             if 'LIMIT' not in sql_upper:
#                 sql_query = f"{sql_query} LIMIT 100"
            
#             print(f"✅ Generated safe SQL: {sql_query}")
#             return sql_query
            
#         except Exception as e:
#             print(f"❌ Error generating SQL: {e}")
#             # Safe fallback
#             if 'count' in query.lower() or 'how many' in query.lower():
#                 return f"SELECT COUNT(*) as count FROM {table_name} {where_clause}"
#             else:
#                 return f"SELECT * FROM {table_name} {where_clause} LIMIT 100"

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
# # TEST THE SERVICE
# # ============================================

# if __name__ == "__main__":
#     print("=" * 60)
#     print("Testing Fixed GroqService")
#     print("=" * 60)
    
#     try:
#         groq = GroqService()
        
#         # Test connection
#         print("\n1. Testing connection...")
#         groq.test_connection()
        
#         # Test SQL generation with various queries
#         print("\n2. Testing SQL generation...")
        
#         table_context = {
#             "table_name": "teachers",
#             "columns": ["id", "employee_id_display", "qualification", "specialization", 
#                        "experience_years", "joining_date", "designation", "salary", "deleted"],
#             "entity_type": "teacher",
#             "row_count": 4,
#             "has_deleted_field": True
#         }
        
#         test_queries = [
#             "how many teachers are there",
#             "show all teachers",
#             "list teachers",
#             "list all teachers",
#             "find teachers with experience > 5",
#             "teachers in math department"
#         ]
        
#         for test_query in test_queries:
#             print(f"\n📝 Query: '{test_query}'")
#             sql = groq.generate_intelligent_sql(test_query, table_context)
#             print(f"   SQL: {sql}")
            
#             # Validate
#             if 'DELETE' in sql.upper():
#                 print("   ❌ FAILED: Contains DELETE")
#             elif not sql.upper().startswith('SELECT'):
#                 print("   ❌ FAILED: Doesn't start with SELECT")
#             else:
#                 print("   ✅ PASSED: Safe SELECT query")
        
#         print("\n" + "=" * 60)
#         print("✅ All tests completed!")
#         print("=" * 60)
        
#     except Exception as e:
#         print(f"\n❌ Test failed: {e}")
#         import traceback
#         traceback.print_exc()




# ============================================
# ULTRA-SIMPLE GROQ SERVICE - NO LLM SQL GENERATION
# File: apps/rag_system/services/groq_service.py
# ============================================

from groq import Groq
from decouple import config
from typing import List, Dict
import os


class GroqService:
    """GROQ Service - ULTRA SIMPLE - NO DELETE ERRORS"""
    
    def __init__(self):
        try:
            api_key = config('GROQ_API_KEY', default=None)
            if not api_key:
                api_key = os.getenv('GROQ_API_KEY')
            
            if not api_key:
                raise ValueError("GROQ_API_KEY not found")
            
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"
            
            print(f"✅ GROQ initialized: {self.model}")
        except Exception as e:
            print(f"❌ GROQ init error: {e}")
            raise
    
    def generate_response(
        self, 
        query: str, 
        context: List[str], 
        system_prompt: str = None
    ) -> Dict:
        """Generate response using GROQ"""
        
        if not system_prompt:
            system_prompt = """You are an LMS assistant. Answer questions clearly and concisely."""
        
        context_str = "\n\n".join([f"Context {i+1}:\n{str(ctx)}" for i, ctx in enumerate(context) if ctx])
        
        messages = [
            {"role": "system", "content": str(system_prompt)},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuery: {query}\n\nAnswer:"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )
            
            answer = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            return {
                "success": True,
                "response": answer,
                "tokens_used": tokens,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "Error processing request.",
                "tokens_used": 0
            }
    
    def generate_intelligent_sql(self, query: str, table_context: Dict) -> str:
        """
        Generate SQL - ULTRA SIMPLE - NO LLM
        
        CRITICAL: We DON'T use LLM at all!
        We just build SQL from simple templates.
        """
        
        table_name = table_context.get("table_name")
        columns = table_context.get("columns", [])
        has_deleted = table_context.get("has_deleted_field", True)
        
        if not table_name:
            print("❌ No table name provided")
            return None
        
        print(f"\n🔧 Building SQL for table: {table_name}")
        
        # Build WHERE clause
        where = ""
        if has_deleted:
            where = " WHERE (deleted = FALSE OR deleted IS NULL)"
        
        # Detect query type from keywords
        query_lower = query.lower()
        
        # Rule 1: COUNT queries
        if any(word in query_lower for word in ['how many', 'count', 'number', 'total']):
            sql = f"SELECT COUNT(*) as count FROM {table_name}{where}"
            print(f"✅ COUNT SQL: {sql}")
            return sql
        
        # Rule 2: LIST/SHOW queries
        elif any(word in query_lower for word in ['list', 'show', 'display', 'get', 'what are', 'all']):
            sql = f"SELECT * FROM {table_name}{where} LIMIT 100"
            print(f"✅ LIST SQL: {sql}")
            return sql
        
        # Rule 3: Default - safe SELECT
        else:
            sql = f"SELECT * FROM {table_name}{where} LIMIT 100"
            print(f"✅ DEFAULT SQL: {sql}")
            return sql
    
    def test_connection(self) -> bool:
        """Test GROQ connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10,
            )
            print("✅ GROQ connection OK")
            return True
        except Exception as e:
            print(f"❌ GROQ connection failed: {e}")
            return False


# TEST
if __name__ == "__main__":
    print("="*60)
    print("Testing ULTRA-SIMPLE GroqService")
    print("="*60)
    
    groq = GroqService()
    
    # Test SQL generation
    table_context = {
        "table_name": "routes",
        "columns": ["id", "name", "code", "start_point", "end_point"],
        "has_deleted_field": True
    }
    
    test_queries = [
        "how many routes",
        "list all routes",
        "what are the routes",
        "show routes"
    ]
    
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        sql = groq.generate_intelligent_sql(q, table_context)
        
        # Validate
        if sql:
            if 'DELETE' in sql.upper():
                print("   ❌ FAILED: Contains DELETE!")
            elif 'UPDATE' in sql.upper():
                print("   ❌ FAILED: Contains UPDATE!")
            elif not sql.upper().startswith('SELECT'):
                print("   ❌ FAILED: Doesn't start with SELECT!")
            else:
                print("   ✅ PASSED: Safe SQL")
        else:
            print("   ❌ FAILED: No SQL generated")
    
    print("\n" + "="*60)
    print("✅ Testing complete")
    print("="*60)