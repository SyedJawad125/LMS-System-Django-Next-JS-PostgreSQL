# ============================================
# FILE 16: apps/rag_system/utils.py
# ============================================

import hashlib
import json
import re
from typing import Dict, Any, List
from datetime import datetime


def create_query_hash(query: str) -> str:
    """Create hash for query caching"""
    return hashlib.sha256(query.encode()).hexdigest()


def format_database_results(results: list) -> str:
    """Format database results for LLM context"""
    if not results:
        return "No results found."
    
    formatted = []
    for i, row in enumerate(results, 1):
        formatted.append(f"Record {i}:")
        for key, value in row.items():
            formatted.append(f"  {key}: {value}")
        formatted.append("")
    
    return "\n".join(formatted)


def extract_sql_from_response(response: str) -> str:
    """Extract SQL query from LLM response"""
    # Remove markdown code blocks
    response = response.replace("```sql", "").replace("```", "")
    
    # Find SQL keywords
    sql_start = response.upper().find("SELECT")
    if sql_start == -1:
        return None
    
    # Extract query
    query = response[sql_start:].strip()
    
    # Remove explanations after query
    if ";" in query:
        query = query[:query.find(";")+1]
    
    return query


def validate_sql_query(query: str) -> bool:
    """Basic SQL query validation"""
    if not query:
        return False
    
    query_upper = query.upper().strip()
    
    # Only allow SELECT queries
    if not query_upper.startswith("SELECT"):
        return False
    
    # Block dangerous keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 
        'ALTER', 'CREATE', 'TRUNCATE', 'EXEC',
        'EXECUTE', 'GRANT', 'REVOKE'
    ]
    if any(keyword in query_upper for keyword in dangerous_keywords):
        return False
    
    return True


def sanitize_sql_query(query: str) -> str:
    """Sanitize SQL query for safety"""
    # Remove comments
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    
    # Remove semicolons (except at end)
    query = query.strip().rstrip(';')
    
    # Remove multiple spaces
    query = ' '.join(query.split())
    
    return query


def calculate_similarity_score(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def format_response_for_display(response: str) -> str:
    """Format response for better readability"""
    # Add bullet points for lists
    lines = response.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('-') and not line.startswith('•'):
            if ':' in line and len(line.split(':')[0].split()) <= 3:
                # Likely a label, keep as is
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def parse_natural_language_date(text: str) -> str:
    """Parse natural language dates to SQL format"""
    text_lower = text.lower()
    today = datetime.now()
    
    if 'today' in text_lower:
        return today.strftime('%Y-%m-%d')
    elif 'yesterday' in text_lower:
        from datetime import timedelta
        yesterday = today - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    elif 'this week' in text_lower:
        return f"date >= '{today.strftime('%Y-%m-%d')}'"
    elif 'this month' in text_lower:
        return f"EXTRACT(MONTH FROM date) = {today.month}"
    
    return text


def extract_entities_from_query(query: str) -> Dict[str, List[str]]:
    """Extract entities (names, dates, numbers) from query"""
    entities = {
        'numbers': [],
        'dates': [],
        'names': [],
        'keywords': []
    }
    
    # Extract numbers
    numbers = re.findall(r'\b\d+\b', query)
    entities['numbers'] = numbers
    
    # Extract potential dates
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}/\d{2}/\d{4}',
        r'\d{1,2}\s+\w+\s+\d{4}'
    ]
    for pattern in date_patterns:
        dates = re.findall(pattern, query)
        entities['dates'].extend(dates)
    
    # Extract capitalized words (potential names)
    names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
    entities['names'] = names
    
    # Extract keywords
    keywords = ['student', 'teacher', 'class', 'fee', 'exam', 'attendance']
    for keyword in keywords:
        if keyword in query.lower():
            entities['keywords'].append(keyword)
    
    return entities


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'


def clean_whitespace(text: str) -> str:
    """Clean excessive whitespace from text"""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """Estimate reading time in minutes"""
    word_count = len(text.split())
    minutes = word_count / wpm
    return max(1, round(minutes))


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency for display"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'PKR': 'Rs.'
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())


def log_query_performance(query: str, response_time: float, success: bool):
    """Log query performance metrics"""
    import logging
    logger = logging.getLogger('rag_system')
    
    log_data = {
        'query': truncate_text(query, 100),
        'response_time': f"{response_time:.2f}s",
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if success:
        logger.info(f"Query successful: {log_data}")
    else:
        logger.error(f"Query failed: {log_data}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Chunk text into overlapping segments"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def safe_json_dumps(obj: Any) -> str:
    """Safely convert object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except Exception as e:
        return json.dumps({'error': str(e)})


def safe_json_loads(text: str) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(text)
    except Exception:
        return {}
