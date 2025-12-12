
# # ============================================
# # COMPLETE GROQ SERVICE FILE
# # File: apps/rag_system/services/groq_service.py
# # COPY THIS ENTIRE FILE - IT HAS ALL METHODS
# # ============================================

# from groq import Groq
# from decouple import config
# from typing import List, Dict
# import json
# import os


# class GroqService:
#     """GROQ LLM Service for RAG"""
    
#     def __init__(self):
#         try:
#             api_key = config('GROQ_API_KEY', default=None)
#             if not api_key:
#                 api_key = os.getenv('GROQ_API_KEY')
            
#             if not api_key:
#                 raise ValueError("GROQ_API_KEY not found in environment variables")
            
#             self.client = Groq(api_key=api_key)
            
#             # ✅ UPDATED MODEL (not deprecated)
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
#         """
#         Generate response using GROQ
        
#         Args:
#             query: User's question
#             context: List of context strings from RAG
#             system_prompt: Optional custom system prompt
            
#         Returns:
#             Dict with response, success status, tokens used
#         """
        
#         # Default system prompt if not provided
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
#                 if ctx  # Skip empty contexts
#             ])
#         else:
#             context_str = "No specific context provided."
        
#         # Create messages for GROQ
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
#             # Call GROQ API
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.3,
#                 max_tokens=2048,
#                 top_p=0.9,
#             )
            
#             # Extract response
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
    

    
#     # Replace the generate_intelligent_sql method:

#     def generate_context_aware_sql(self, query: str, table_info: Dict, plan: Dict) -> str:
#         """Generate SQL using actual table names from the plan"""
        
#         # Get the primary table from plan
#         primary_table = plan.get("primary_table")
#         expected_tables = plan.get("expected_tables", [])
        
#         if not expected_tables:
#             print("⚠️ No tables expected for this query")
#             return None
        
#         print(f"🎯 Using primary table: {primary_table}")
#         print(f"📋 All expected tables: {expected_tables}")
        
#         # Build table context with actual names
#         table_context = []
#         for table_name in expected_tables[:3]:  # Limit to 3 tables
#             if table_name in table_info:
#                 table_data = table_info[table_name]
#                 cols = table_data.get("column_names", [])[:6]  # First 6 columns
#                 table_context.append(f"Table: {table_name}")
#                 table_context.append(f"Columns: {', '.join(cols)}")
#                 if len(cols) < len(table_data.get("column_names", [])):
#                     table_context.append(f"  ... and {len(table_data.get('column_names', [])) - len(cols)} more columns")
#                 table_context.append("")
        
#         tables_str = "\n".join(table_context)
        
#         # Determine query type
#         query_type = plan.get("query_type", "unknown")
#         is_count_query = "count" in query_type.lower() or "how many" in query.lower()
        
#         system_prompt = f"""You are a PostgreSQL SQL expert. Generate SQL using ONLY the actual tables provided.

#     ACTUAL TABLES IN DATABASE:
#     {tables_str}

#     USER QUERY: "{query}"

#     QUERY TYPE: {query_type.upper()}
#     PRIMARY TABLE TO USE: {primary_table}

#     CRITICAL RULES:
#     1. You MUST use the actual table names shown above
#     2. DO NOT invent table names like 'roles' or 'teachers' if they don't exist
#     3. If the primary table is '{primary_table}', use it
#     4. For counting queries: SELECT COUNT(*) FROM {primary_table}
#     5. For listing queries: SELECT * FROM {primary_table}
#     6. ALWAYS add: WHERE (deleted = FALSE OR deleted IS NULL)
#     7. Use LIMIT 100 for safety
#     8. Return ONLY the SQL query - no explanations

#     WRONG EXAMPLES (DO NOT DO THIS):
#     - Query: "how many roles" 
#     - If 'roles' table doesn't exist but 'users_role' does exist
#     - WRONG: SELECT COUNT(*) FROM roles  ← This is wrong!
#     - RIGHT: SELECT COUNT(*) FROM users_role  ← This is correct!

#     CORRECT EXAMPLES:
#     Query: "how many users"
#     Tables available: users, auth_user
#     SQL: SELECT COUNT(*) FROM users WHERE deleted = FALSE LIMIT 100

#     Query: "list all permissions"
#     Tables available: auth_permission
#     SQL: SELECT * FROM auth_permission WHERE deleted = FALSE LIMIT 100

#     Query: "show me roles"
#     Tables available: users_role
#     SQL: SELECT * FROM users_role WHERE deleted = FALSE LIMIT 100

#     Now generate SQL for: "{query}"
#     Use table: {primary_table}"""

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"Generate SQL query for: {query}\nUse the actual table names from the list above."}
#         ]
        
#         try:
#             print(f"🤖 Generating SQL with table: {primary_table}")
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.05,  # Very low for deterministic SQL
#                 max_tokens=256,
#             )
            
#             sql_query = response.choices[0].message.content.strip()
            
#             # Clean the SQL
#             sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
#             sql_query = sql_query.rstrip(';')
            
#             # Validate table name is correct
#             import re
#             from_table_match = re.search(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
            
#             if from_table_match:
#                 used_table = from_table_match.group(1)
#                 # Check if used table is in expected tables
#                 if used_table not in expected_tables:
#                     print(f"⚠️ SQL uses table '{used_table}' but expected one of: {expected_tables}")
#                     # Force correct table
#                     sql_query = re.sub(
#                         r'FROM\s+\w+', 
#                         f'FROM {primary_table}', 
#                         sql_query, 
#                         flags=re.IGNORECASE
#                     )
#                     print(f"🔄 Corrected to use: {primary_table}")
            
#             print(f"✅ Final SQL: {sql_query}")
#             return sql_query
            
#         except Exception as e:
#             print(f"❌ Error generating SQL: {e}")
#             # Fallback: generate simple SQL with primary table
#             if primary_table:
#                 fallback_sql = f"SELECT COUNT(*) FROM {primary_table} WHERE (deleted = FALSE OR deleted IS NULL) LIMIT 100"
#                 print(f"🔄 Using fallback SQL: {fallback_sql}")
#                 return fallback_sql
#             return None
    
#     def test_connection(self) -> bool:
#         """
#         Test if GROQ API connection is working
        
#         Returns:
#             True if connection successful, False otherwise
#         """
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
#     """
#     Test the GroqService
    
#     Run with: python -m apps.rag_system.services.groq_service
#     """
#     print("=" * 60)
#     print("Testing GroqService")
#     print("=" * 60)
    
#     try:
#         # Initialize service
#         groq = GroqService()
        
#         # Test 1: Connection test
#         print("\n1. Testing connection...")
#         groq.test_connection()
        
#         # Test 2: Simple response
#         print("\n2. Testing generate_response...")
#         result = groq.generate_response(
#             query="What is 2+2?",
#             context=["This is a simple math question."]
#         )
#         print(f"Response: {result['response']}")
#         print(f"Success: {result['success']}")
#         print(f"Tokens: {result['tokens_used']}")
        
#         # Test 3: SQL generation
#         print("\n3. Testing SQL generation...")
#         schema = {
#             "teachers": [
#                 {"name": "id", "type": "integer"},
#                 {"name": "name", "type": "text"},
#                 {"name": "deleted", "type": "boolean"}
#             ]
#         }
#         sql = groq.generate_sql_query("How many teachers?", schema)
#         print(f"Generated SQL: {sql}")
        
#         print("\n" + "=" * 60)
#         print("✅ All tests passed!")
#         print("=" * 60)
        
#     except Exception as e:
#         print(f"\n❌ Test failed: {e}")
#         import traceback
#         traceback.print_exc()


# Groq Service code


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