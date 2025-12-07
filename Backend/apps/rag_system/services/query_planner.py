# NEW FILE - Create this

from typing import Dict, List, Any
from enum import Enum


class QueryType(Enum):
    COUNT = "count"          # how many, count, total
    LIST = "list"           # show, list, display
    DETAIL = "detail"       # get, find, search for
    ANALYTICAL = "analytical"  # analyze, compare, summarize
    UNKNOWN = "unknown"


class QueryPlanner:
    """Plan and execute intelligent queries"""
    
    def __init__(self, db_connector):
        self.db = db_connector
    
    def plan_query_execution(self, query: str) -> Dict:
        """Create detailed execution plan"""
        query_lower = query.lower()
        
        # Determine query type
        query_type = self._determine_query_type(query_lower)
        
        # Discover relevant tables
        expected_tables = self.db.discover_relevant_tables(query)
        
        # Create execution steps
        steps = []
        
        if expected_tables and query_type in [QueryType.COUNT, QueryType.LIST, QueryType.DETAIL]:
            steps.append(f"Query {expected_tables[0]} table for {query_type.value} information")
            if len(expected_tables) > 1:
                steps.append(f"Also check {expected_tables[1]} table if needed")
        
        if query_type == QueryType.COUNT:
            steps.append("Count results and return total")
        elif query_type == QueryType.LIST:
            steps.append("Format results as a list")
        
        steps.append("Generate final response with LLM")
        
        return {
            "query_type": query_type.value,
            "expected_tables": expected_tables,
            "steps": steps,
            "needs_sql": bool(expected_tables),
            "needs_vector_search": not bool(expected_tables),
            "primary_table": expected_tables[0] if expected_tables else None
        }
    
    def _determine_query_type(self, query_lower: str) -> QueryType:
        """Determine what type of query this is"""
        if any(word in query_lower for word in ['how many', 'count', 'total', 'number of']):
            return QueryType.COUNT
        elif any(word in query_lower for word in ['show', 'list', 'display', 'get all', 'get me']):
            return QueryType.LIST
        elif any(word in query_lower for word in ['find', 'search', 'get', 'tell me about']):
            return QueryType.DETAIL
        elif any(word in query_lower for word in ['analyze', 'compare', 'summarize', 'trend']):
            return QueryType.ANALYTICAL
        else:
            return QueryType.UNKNOWN
    
    def get_table_info_for_sql(self, table_names: List[str]) -> Dict:
        """Get detailed information about tables for SQL generation"""
        table_info = {}
        
        for table_name in table_names[:2]:  # Limit to first 2 tables
            schema = self.db.get_table_schema_details(table_name)
            if schema:
                # Get sample data to understand content
                sample = self.db.get_table_sample_data(table_name, limit=2)
                
                table_info[table_name] = {
                    "schema": schema,
                    "sample_rows": sample,
                    "column_names": [col["name"] for col in schema.get("columns", [])],
                    "has_deleted_column": any(
                        col["name"].lower() == "deleted" 
                        for col in schema.get("columns", [])
                    )
                }
        
        return table_info