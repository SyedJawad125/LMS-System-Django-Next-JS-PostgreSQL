# ============================================
# ENHANCED SYSTEM PROMPT HANDLER
# File: apps/rag_system/services/prompt_handler.py
# ============================================

"""
Handles system prompts with special logic for different query types
Especially important for role/permission queries
"""

from typing import List, Dict


class SystemPromptHandler:
    """Creates optimized system prompts based on query type and context"""
    
    @staticmethod
    def create_prompt(
        query: str,
        context_sources: Dict,
        has_database_results: bool = False,
        has_api_data: bool = False
    ) -> str:
        """
        Create appropriate system prompt based on query characteristics
        
        Args:
            query: User's query
            context_sources: Information about what data is available
            has_database_results: Whether database query results are available
            has_api_data: Whether API data (like roles/permissions) is in context
            
        Returns:
            Optimized system prompt
        """
        query_lower = query.lower()
        
        # Detect query type
        is_permission_query = SystemPromptHandler._is_permission_query(query_lower)
        is_role_query = SystemPromptHandler._is_role_query(query_lower)
        is_count_query = SystemPromptHandler._is_count_query(query_lower)
        is_list_query = SystemPromptHandler._is_list_query(query_lower)
        
        # Choose appropriate prompt template
        if is_permission_query or is_role_query:
            return SystemPromptHandler._permission_role_prompt(
                query, has_api_data
            )
        elif has_database_results:
            return SystemPromptHandler._database_results_prompt(
                query, is_count_query, is_list_query
            )
        else:
            return SystemPromptHandler._general_prompt(query)
    
    @staticmethod
    def _is_permission_query(query_lower: str) -> bool:
        """Check if query is about permissions"""
        permission_keywords = [
            'permission', 'permissions', 'access', 'rights',
            'allowed', 'can do', 'able to', 'privileges',
            'what can', 'capabilities'
        ]
        return any(kw in query_lower for kw in permission_keywords)
    
    @staticmethod
    def _is_role_query(query_lower: str) -> bool:
        """Check if query is about roles"""
        role_keywords = [
            'role', 'roles', 'teacher', 'student', 'parent',
            'super', 'admin', 'user type'
        ]
        return any(kw in query_lower for kw in role_keywords)
    
    @staticmethod
    def _is_count_query(query_lower: str) -> bool:
        """Check if query is asking for counts"""
        count_keywords = ['how many', 'count', 'number of', 'total']
        return any(kw in query_lower for kw in count_keywords)
    
    @staticmethod
    def _is_list_query(query_lower: str) -> bool:
        """Check if query is asking for a list"""
        list_keywords = ['list', 'show', 'display', 'what are']
        return any(kw in query_lower for kw in list_keywords)
    
    @staticmethod
    def _permission_role_prompt(query: str, has_api_data: bool) -> str:
        """Prompt for permission/role queries"""
        
        prompt = """You are an LMS permissions expert. You have access to ACTUAL role and permission data.

🔴 CRITICAL INSTRUCTIONS FOR PERMISSION/ROLE QUERIES:

1. **USE THE PROVIDED DATA** - You have REAL role and permission information in your context
2. **BE SPECIFIC** - List the EXACT permissions from the data provided
3. **DO NOT HALLUCINATE** - Only mention permissions that are explicitly in the context
4. **FORMAT CLEARLY** - Present permissions in an organized, readable way

📋 HOW TO ANSWER:

For "What permissions does [ROLE] have?":
- Find the role information in your context
- List ALL permissions for that role
- Group them by category if helpful
- Include permission names and codes if available

For "What can a [ROLE] do?":
- Find the role's permissions
- Explain what actions those permissions enable
- Be specific about capabilities

⚠️ IMPORTANT RULES:
- If you see role/permission data in context marked as "ROLE:" → USE IT
- Count the permissions accurately from the provided data
- If a role has 3 permissions, say exactly 3, not "typically" or "usually"
- Include actual permission names like "Read Student", "Create User", etc.

❌ DO NOT:
- Say "typically includes" or "usually has"
- List generic permissions not in the data
- Make assumptions about what a role "should" have
- Say "I don't have access" when the data IS in your context

✅ DO:
- List EXACT permissions from the context
- Be precise with counts and names
- Quote actual permission codes if available
- Organize by category for readability

"""
        
        if has_api_data:
            prompt += """
🟢 **YOU HAVE ACTUAL ROLE DATA IN YOUR CONTEXT**

Look for sections marked:
- "ROLE: [name]"
- "PERMISSIONS ([number] total):"
- Permission lists with names and codes

Use this data DIRECTLY in your answer.
"""
        else:
            prompt += """
⚠️ If you don't see specific role/permission data in the context, say:
"I don't see the specific permission data for this role in my current context. 
Please ensure the role data has been loaded into the system."
"""
        
        prompt += f"\n\nUSER QUERY: '{query}'\n\nProvide a clear, accurate answer based on the data in your context."
        
        return prompt
    
    @staticmethod
    def _database_results_prompt(
        query: str,
        is_count: bool,
        is_list: bool
    ) -> str:
        """Prompt for queries with database results"""
        
        prompt = """You are an LMS data analyst. You have ACTUAL DATABASE QUERY RESULTS.

🔴 CRITICAL INSTRUCTIONS:

⚠️ **YOU HAVE REAL DATA** - The section marked 'ACTUAL DATABASE QUERY RESULTS' contains REAL DATA
⚠️ **USE THIS DATA** - Answer directly from the results provided
⚠️ **BE SPECIFIC** - Give exact numbers and values from the data

"""
        
        if is_count:
            prompt += """
FOR COUNTING QUERIES:
- Look for the count value in the results
- State the exact number
- Example: "There are 247 students in the system."

"""
        elif is_list:
            prompt += """
FOR LISTING QUERIES:
- Show the actual records from the results
- Include relevant fields (name, email, etc.)
- Limit to first 10-15 if there are many
- Example: "Here are the users: 1. John (john@example.com), 2. Jane..."

"""
        
        prompt += """
❌ DO NOT:
- Say "not available in provided data"
- Say "I would need access to"
- Be vague or speculative

✅ DO:
- Give concrete answers from the data
- List specific values
- Be direct and factual

"""
        
        prompt += f"\n\nUSER QUERY: '{query}'\n\nAnswer using the database results in your context."
        
        return prompt
    
    @staticmethod
    def _general_prompt(query: str) -> str:
        """General prompt for other queries"""
        
        return f"""You are a helpful LMS assistant.

Answer the user's question using the information available in your context.

Be direct, accurate, and helpful. If you don't have specific information, 
explain what you do know and suggest how the user might get more details.

USER QUERY: '{query}'

Provide a clear, helpful answer."""


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("Testing System Prompt Handler")
    print("="*70)
    
    test_queries = [
        ("What permissions does teacher have?", True, False),
        ("How many users?", False, True),
        ("List all students", False, True),
        ("What is an LMS?", False, False),
    ]
    
    for query, has_api, has_db in test_queries:
        print(f"\n📝 Query: {query}")
        print(f"   Has API data: {has_api}")
        print(f"   Has DB results: {has_db}")
        
        prompt = SystemPromptHandler.create_prompt(
            query, 
            {},
            has_database_results=has_db,
            has_api_data=has_api
        )
        
        print(f"   Prompt length: {len(prompt)} chars")
        print(f"   Preview: {prompt[:150]}...")
    
    print("\n" + "="*70)
    print("✅ Tests complete!")
    print("="*70)