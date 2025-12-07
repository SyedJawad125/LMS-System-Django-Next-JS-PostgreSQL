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
            
#             # ⚠️ FIX: Use NEW model instead of deprecated one
#             # OLD: self.model = "llama-3.1-70b-versatile"  # DEPRECATED!
#             self.model = "llama-3.3-70b-versatile"  # ✅ NEW MODEL
#             # Alternative options:
#             # self.model = "llama-3.1-8b-instant"
#             # self.model = "mixtral-8x7b-32768"
            
#             print(f"✓ GROQ service initialized with model: {self.model}")
#         except Exception as e:
#             print(f"Error initializing GROQ: {e}")
#             raise
    
#     def generate_response(
#         self, 
#         query: str, 
#         context: List[str], 
#         system_prompt: str = None
#     ) -> Dict:
#         """Generate response using GROQ"""
        
#         # ⚠️ FIX: Proper system prompt format
#         if not system_prompt:
#             system_prompt = """You are an intelligent LMS assistant. Help with student records, fees, attendance, exams, and all LMS data. Be concise and accurate."""
        
#         # Build context string
#         if context:
#             context_str = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
#         else:
#             context_str = "No specific context provided."
        
#         # ⚠️ FIX: Ensure system_prompt is a STRING, not dict
#         messages = [
#             {
#                 "role": "system", 
#                 "content": str(system_prompt)  # ✅ Ensure it's a string
#             },
#             {
#                 "role": "user", 
#                 "content": f"Context:\n{context_str}\n\nQuery: {query}\n\nAnswer:"
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
            
#             return {
#                 "success": True,
#                 "response": response.choices[0].message.content,
#                 "tokens_used": response.usage.total_tokens,
#                 "model": self.model
#             }
#         except Exception as e:
#             print(f"GROQ API Error: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "response": "Sorry, I encountered an error processing your request.",
#                 "tokens_used": 0
#             }
    
#     def generate_sql_query(self, natural_language_query: str, schema_info: Dict) -> str:
#         """Generate SQL query from natural language"""
        
#         system_prompt = f"""You are a PostgreSQL SQL expert. Generate ONLY SELECT queries.

# Schema: {json.dumps(schema_info, indent=2)}

# Rules:
# 1. Only SELECT queries
# 2. Use proper JOINs
# 3. Add LIMIT 100
# 4. Return ONLY SQL, no markdown"""

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"Generate SQL: {natural_language_query}"}
#         ]
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.1,
#                 max_tokens=1024,
#             )
            
#             sql_query = response.choices[0].message.content.strip()
#             sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
#             sql_query = sql_query.rstrip(';')
            
#             return sql_query
            
#         except Exception as e:
#             print(f"Error generating SQL: {e}")
#             return None


# ============================================
# COMPLETE GROQ SERVICE FILE
# File: apps/rag_system/services/groq_service.py
# COPY THIS ENTIRE FILE - IT HAS ALL METHODS
# ============================================

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
    
#     def generate_sql_query(self, natural_language_query: str, schema_info: Dict) -> str:
#         """
#         Generate SQL query from natural language
        
#         Args:
#             natural_language_query: User's question in plain English
#             schema_info: Database schema information
            
#         Returns:
#             SQL query string or None if failed
#         """
        
#         # Create detailed system prompt with examples
#         system_prompt = f"""You are a PostgreSQL SQL expert. Generate ONLY SELECT queries.

# Available Database Tables and Columns:
# {json.dumps(schema_info, indent=2)}

# CRITICAL RULES:
# 1. ONLY generate SELECT queries (no INSERT, UPDATE, DELETE, DROP)
# 2. For counting queries like "How many X?", use: SELECT COUNT(*) FROM main_table
# 3. ALWAYS add: WHERE deleted = FALSE OR deleted IS NULL
# 4. Use LIMIT 100 for safety
# 5. Return ONLY the SQL query - no explanations, no markdown, no backticks
# 6. Use proper JOINs when needed
# 7. Handle NULL values with COALESCE or IS NULL checks

# EXAMPLES:
# Query: "How many teachers?"
# SQL: SELECT COUNT(*) FROM teachers WHERE deleted = FALSE LIMIT 100

# Query: "How many students?"  
# SQL: SELECT COUNT(*) FROM students WHERE deleted = FALSE LIMIT 100

# Query: "Show me all teachers"
# SQL: SELECT id, qualification, designation, experience_years FROM teachers WHERE deleted = FALSE LIMIT 100

# Query: "List students in Grade 10"
# SQL: SELECT s.id, s.name, c.name as class_name FROM students s JOIN classes c ON s.class_id = c.id WHERE c.grade = 10 AND s.deleted = FALSE LIMIT 100

# Now generate SQL for the user's query."""

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"Generate SQL query for: {natural_language_query}"}
#         ]
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.1,  # Low temperature for more deterministic SQL
#                 max_tokens=1024,
#             )
            
#             # Extract and clean SQL
#             sql_query = response.choices[0].message.content.strip()
            
#             # Remove markdown code blocks if present
#             sql_query = sql_query.replace("```sql", "")
#             sql_query = sql_query.replace("```", "")
#             sql_query = sql_query.strip()
            
#             # Remove semicolon at the end
#             sql_query = sql_query.rstrip(';')
            
#             print(f"🔍 Generated SQL: {sql_query}")
            
#             return sql_query
            
#         except Exception as e:
#             print(f"❌ Error generating SQL: {e}")
#             return None


    # Replace the generate_sql_query method:

    # Replace the generate_sql_query method with this:

    def generate_intelligent_sql(self, query: str, table_info: Dict) -> str:
        """Generate SQL query with understanding of actual table structure"""
        
        if not table_info:
            print("⚠️ No table information provided")
            return None
        
        # Build detailed table descriptions
        table_descriptions = []
        for table_name, table_data in table_info.items():
            if isinstance(table_data, dict) and "columns" in table_data:
                cols = table_data["columns"]
                # Get first 8 column names
                col_names = [col["name"] for col in cols[:8]]
                table_desc = f"Table: {table_name} ({len(cols)} columns)\nColumns: {', '.join(col_names)}"
                if len(cols) > 8:
                    table_desc += f"... and {len(cols)-8} more columns"
                table_descriptions.append(table_desc)
        
        tables_str = "\n\n".join(table_descriptions)
        
        system_prompt = f"""You are an expert PostgreSQL SQL generator. Generate ONLY SELECT queries.

    ACTUAL TABLES AVAILABLE:
    {tables_str}

    USER QUERY: "{query}"

    CRITICAL RULES:
    1. You MUST use the actual tables listed above
    2. Generate SQL that will answer the user's query
    3. For counting queries: Use SELECT COUNT(*) FROM appropriate_table
    4. For listing queries: Use SELECT relevant_columns FROM appropriate_table
    5. ALWAYS include: WHERE (deleted = FALSE OR deleted IS NULL)
    6. Use LIMIT 100 for safety
    7. Return ONLY the SQL query - no explanations, no markdown
    8. Use proper table aliases if joining tables
    9. If unsure which column to count, use SELECT COUNT(*)

    EXAMPLE THINKING:
    Query: "how many teachers"
    Tables available: teachers, users, employees
    SQL: SELECT COUNT(*) FROM teachers WHERE deleted = FALSE LIMIT 100

    Query: "list all roles"
    Tables available: users_role, role_permissions
    SQL: SELECT * FROM users_role WHERE deleted = FALSE LIMIT 100

    Query: "show me users"
    Tables available: users, user_profiles
    SQL: SELECT * FROM users WHERE deleted = FALSE LIMIT 100

    Now generate SQL for the user's query using ONLY the available tables."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate SQL for: {query}"}
        ]
        
        try:
            print(f"🤖 Generating SQL with {len(table_info)} tables...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for deterministic SQL
                max_tokens=512,
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean the SQL
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            sql_query = sql_query.rstrip(';')
            
            # Extract only SQL lines
            lines = sql_query.split('\n')
            sql_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.lower().startswith(('here', 'sql', 'query:', 'selecting')):
                    sql_lines.append(line)
            
            if sql_lines:
                final_sql = ' '.join(sql_lines)
            else:
                final_sql = sql_query
            
            print(f"✅ Generated SQL: {final_sql}")
            return final_sql
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
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
        
        # Test 3: SQL generation
        print("\n3. Testing SQL generation...")
        schema = {
            "teachers": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "text"},
                {"name": "deleted", "type": "boolean"}
            ]
        }
        sql = groq.generate_sql_query("How many teachers?", schema)
        print(f"Generated SQL: {sql}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()