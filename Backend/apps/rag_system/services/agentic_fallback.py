# NEW FILE: Create this file
from typing import Dict


class AgenticFallback:
    """Handle cases where primary methods fail"""
    
    def __init__(self, groq_service):
        self.groq = groq_service
    
    def analyze_and_suggest(self, query: str, failed_results: Dict) -> Dict:
        """Analyze why query failed and suggest alternatives"""
        
        system_prompt = """You are a query analysis assistant. Analyze why a database query failed and suggest alternatives.

COMMON ISSUES:
1. Table doesn't exist - suggest similar tables
2. Column doesn't exist - suggest similar columns
3. No data available - suggest where data might be stored
4. Query too complex - suggest simpler query

Provide:
1. Analysis of likely issue
2. Alternative table/column names to try
3. Suggested rephrased query"""

        analysis_query = f"""
Original Query: {query}
Failure Details: {failed_results}

Analyze the issue and suggest alternatives.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_query}
        ]
        
        try:
            response = self.groq.client.chat.completions.create(
                model=self.groq.model,
                messages=messages,
                temperature=0.3,
                max_tokens=512,
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "suggestion": "Try rephrasing or ask about specific tables that exist."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }