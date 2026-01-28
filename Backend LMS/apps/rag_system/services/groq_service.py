# # ============================================
# # ULTRA-SIMPLE GROQ SERVICE - NO LLM SQL GENERATION
# # File: apps/rag_system/services/groq_service.py
# # ============================================

# import os
# from groq import Groq
# from decouple import config
# from typing import List, Dict
# import logging

# # Set up logging to catch key errors in your terminal
# logger = logging.getLogger(__name__)

# class GroqService:
#     """
#     FIXED GROQ SERVICE
#     - Enhanced API Key detection
#     - Safe SQL generation based on your actual PostgreSQL images
#     """
    
#     def __init__(self):
#         self.client = None
#         self.model = "llama-3.3-70b-versatile"
        
#         # 1. ATTEMPT TO LOAD API KEY (Multi-method fallback)
#         api_key = None
        
#         # Try python-decouple (.env file)
#         try:
#             api_key = config('GROQ_API_KEY', default=None)
#         except Exception:
#             pass
            
#         # Try OS environment variables
#         if not api_key:
#             api_key = os.getenv('GROQ_API_KEY')
            
#         # 2. VALIDATE KEY AND INITIALIZE
#         if api_key and api_key != "None" and len(api_key) > 10:
#             try:
#                 self.client = Groq(api_key=api_key)
#                 # Quick validation call
#                 print(f"✅ GROQ Service Connected: {self.model}")
#             except Exception as e:
#                 print(f"❌ GROQ Initialization Failed: {str(e)}")
#         else:
#             print("❌ ERROR: GROQ_API_KEY is missing or invalid in your .env file!")

#     def generate_response(self, query: str, context: List[str], system_prompt: str = None) -> Dict:
#         """Generate response with safety check for active client"""
#         if not self.client:
#             return {
#                 "success": False, 
#                 "response": "I cannot answer right now because the AI API key is not configured correctly.",
#                 "error": "No Groq client initialized"
#             }
        
#         if not system_prompt:
#             system_prompt = "You are a helpful School Management Assistant. Use the provided context to answer questions."
        
#         context_str = "\n\n".join([f"Data Source {i+1}:\n{str(ctx)}" for i, ctx in enumerate(context) if ctx])
        
#         messages = [
#             {"role": "system", "content": str(system_prompt)},
#             {"role": "user", "content": f"Context Information:\n{context_str}\n\nUser Question: {query}\n\nHelpful Answer:"}
#         ]
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.2, # Lower temperature for more factual answers
#                 max_tokens=1024,
#             )
            
#             return {
#                 "success": True,
#                 "response": response.choices[0].message.content,
#                 "model": self.model
#             }
#         except Exception as e:
#             logger.error(f"Groq Generation Error: {e}")
#             return {"success": False, "error": str(e), "response": "Sorry, I hit an error processing that."}

#     def generate_intelligent_sql(self, query: str, table_context: Dict) -> str:
#         table_name = table_context.get("table_name", "routes")
        
#         # Based on your image: 
#         # false = Not deleted (Active)
#         # true = Deleted
#         where_clause = ' WHERE "deleted" = false'
        
#         query_lower = query.lower()

#         # Rule: List routes
#         if any(word in query_lower for word in ['what are', 'list', 'show', 'routes']):
#             return f'SELECT name, code, start_point, end_point FROM "{table_name}"{where_clause} LIMIT 50;'
        
#         # Rule: Count active routes
#         if "how many" in query_lower:
#             return f'SELECT COUNT(*) FROM "{table_name}"{where_clause};'

#         return f'SELECT * FROM "{table_name}"{where_clause} LIMIT 10;'

#     def test_connection(self) -> bool:
#         """Used for diagnostic.py to check if the key works"""
#         if not self.client: return False
#         try:
#             self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[{"role": "user", "content": "hi"}],
#                 max_tokens=5
#             )
#             return True
#         except:
#             return False

# # TEST
# if __name__ == "__main__":
#     print("="*60)
#     print("Testing ULTRA-SIMPLE GroqService")
#     print("="*60)
    
#     groq = GroqService()
    
#     # Test SQL generation
#     table_context = {
#         "table_name": "routes",
#         "columns": ["id", "name", "code", "start_point", "end_point"],
#         "has_deleted_field": True
#     }
    
#     test_queries = [
#         "how many routes",
#         "list all routes",
#         "what are the routes",
#         "show routes"
#     ]
    
#     for q in test_queries:
#         print(f"\nQuery: '{q}'")
#         sql = groq.generate_intelligent_sql(q, table_context)
        
#         # Validate
#         if sql:
#             if 'DELETE' in sql.upper():
#                 print("   ❌ FAILED: Contains DELETE!")
#             elif 'UPDATE' in sql.upper():
#                 print("   ❌ FAILED: Contains UPDATE!")
#             elif not sql.upper().startswith('SELECT'):
#                 print("   ❌ FAILED: Doesn't start with SELECT!")
#             else:
#                 print("   ✅ PASSED: Safe SQL")
#         else:
#             print("   ❌ FAILED: No SQL generated")
    
#     print("\n" + "="*60)
#     print("✅ Testing complete")
#     print("="*60)





# ============================================
# FINAL FIXED GROQ SERVICE
# File: apps/rag_system/services/groq_service.py
# ============================================

from groq import Groq
from decouple import config
from typing import List, Dict
import os


class GroqService:
    """FINAL FIXED - Handles boolean 'deleted' column correctly"""
    
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
            system_prompt = """You are an LMS assistant. Answer questions using the actual data provided in the context."""
        
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
        Generate SQL - HANDLES BOOLEAN DELETED CORRECTLY
        
        Your database uses:
        - deleted = false (active records)
        - deleted = true (deleted records)
        """
        
        table_name = table_context.get("table_name")
        has_deleted = table_context.get("has_deleted_field", True)
        
        if not table_name:
            print("❌ No table name")
            return None
        
        print(f"\n🔧 Building SQL for: {table_name}")
        
        # Build WHERE clause with CORRECT boolean syntax
        where = ""
        if has_deleted:
            # Use lowercase 'false' for PostgreSQL boolean
            where = " WHERE deleted = false"
        
        query_lower = query.lower()
        
        # Rule 1: COUNT queries
        if any(word in query_lower for word in ['how many', 'count', 'number', 'total']):
            sql = f"SELECT COUNT(*) as count FROM {table_name}{where}"
            print(f"✅ COUNT: {sql}")
            return sql
        
        # Rule 2: LIST queries  
        elif any(word in query_lower for word in ['list', 'show', 'display', 'get', 'what are', 'all']):
            sql = f"SELECT * FROM {table_name}{where} LIMIT 100"
            print(f"✅ LIST: {sql}")
            return sql
        
        # Rule 3: Default
        else:
            sql = f"SELECT * FROM {table_name}{where} LIMIT 100"
            print(f"✅ DEFAULT: {sql}")
            return sql
    
    def test_connection(self) -> bool:
        """Test connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10,
            )
            print("✅ GROQ OK")
            return True
        except Exception as e:
            print(f"❌ GROQ failed: {e}")
            return False


# TEST
if __name__ == "__main__":
    print("="*60)
    print("Testing FINAL FIXED GroqService")
    print("="*60)
    
    groq = GroqService()
    
    table_context = {
        "table_name": "routes",
        "columns": ["id", "name", "code", "start_point", "end_point", "deleted"],
        "has_deleted_field": True
    }
    
    test_queries = [
        "how many routes",
        "what are the routes",
        "list all routes"
    ]
    
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        sql = groq.generate_intelligent_sql(q, table_context)
        
        if sql:
            # Check for issues
            if 'DELETE FROM' in sql.upper():
                print("   ❌ FAIL: DELETE command")
            elif 'UPDATE' in sql.upper():
                print("   ❌ FAIL: UPDATE command")
            elif not sql.upper().startswith('SELECT'):
                print("   ❌ FAIL: Not SELECT")
            elif 'deleted = false' not in sql.lower():
                print("   ⚠️  WARNING: Missing deleted filter")
            else:
                print("   ✅ PASS: Safe SQL with correct boolean")
    
    print("\n" + "="*60)