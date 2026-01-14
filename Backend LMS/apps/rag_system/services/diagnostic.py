# ============================================
# DIAGNOSTIC SCRIPT - Find the Issue
# File: apps/rag_system/services/diagnostic.py
# ============================================

"""
Run this to diagnose why SQL execution is failing

Usage:
python -m apps.rag_system.services.diagnostic
"""

from .database_connector import DatabaseConnector
from .groq_service import GroqService
from .query_executor import QueryExecutor
from .vectorstore_service import VectorStoreService


def test_database_connector():
    """Test if database connector works"""
    print("\n" + "="*60)
    print("TEST 1: Database Connector")
    print("="*60)
    
    try:
        db = DatabaseConnector()
        
        # Test 1: Get all tables
        tables = db.get_all_tables()
        print(f"✅ Found {len(tables)} tables")
        print(f"   Sample: {tables[:5]}")
        
        # Test 2: Check if 'students' table exists
        if 'students' in tables:
            print(f"✅ 'students' table exists")
            
            # Test 3: Get schema
            schema = db.get_table_schema_info('students')
            print(f"✅ Schema retrieved:")
            print(f"   Columns: {schema.get('columns', [])[:5]}")
            print(f"   Row count: {schema.get('row_count', 0)}")
            print(f"   Entity type: {schema.get('entity_type', 'unknown')}")
            
            # Test 4: Try a simple query
            sql = "SELECT COUNT(*) as count FROM students WHERE (deleted = FALSE OR deleted IS NULL)"
            results = db.execute_query(sql)
            print(f"✅ Query executed:")
            print(f"   SQL: {sql}")
            print(f"   Results: {results}")
            
            return True
        else:
            print(f"❌ 'students' table NOT found!")
            print(f"   Available tables: {tables}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_executor():
    """Test if query executor works"""
    print("\n" + "="*60)
    print("TEST 2: Query Executor")
    print("="*60)
    
    try:
        executor = QueryExecutor()
        
        # Prepare table context
        db = DatabaseConnector()
        schema = db.get_table_schema_info('students')
        
        table_context = {
            "table_name": "students",
            "columns": schema.get("columns", []),
            "entity_type": "student",
            "row_count": schema.get("row_count", 0)
        }
        
        print(f"Table context:")
        print(f"   Table: {table_context['table_name']}")
        print(f"   Columns: {table_context['columns'][:5]}...")
        print(f"   Entity: {table_context['entity_type']}")
        
        # Test query
        query = "how many students are enrolled and their admission numbers"
        print(f"\nQuery: '{query}'")
        
        result = executor.execute_user_query(query, table_context)
        
        print(f"\nResult:")
        print(f"   Success: {result['success']}")
        print(f"   SQL: {result['sql']}")
        print(f"   Row count: {result['row_count']}")
        print(f"   Error: {result.get('error')}")
        
        if result['success'] and result['results']:
            print(f"   Sample results: {result['results'][:3]}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sql_generation():
    """Test if SQL generation works"""
    print("\n" + "="*60)
    print("TEST 3: SQL Generation")
    print("="*60)
    
    try:
        groq = GroqService()
        db = DatabaseConnector()
        schema = db.get_table_schema_info('students')
        
        table_context = {
            "table_name": "students",
            "columns": schema.get("columns", []),
            "entity_type": "student"
        }
        
        queries = [
            "how many students",
            "show all students",
            "list student admission numbers",
            "how many students are enrolled and their admission numbers"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            sql = groq.generate_intelligent_sql(query, table_context)
            print(f"   SQL: {sql}")
            
            if sql:
                # Validate
                if 'admission_number' in query.lower():
                    if 'admission_number' not in sql.lower():
                        print(f"   ⚠️ WARNING: Query asks for admission_number but SQL doesn't include it!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_table_discovery():
    """Test if table discovery works"""
    print("\n" + "="*60)
    print("TEST 4: Table Discovery")
    print("="*60)
    
    try:
        db = DatabaseConnector()
        
        queries = [
            "how many students",
            "how many students are enrolled and their admission numbers",
            "show all students",
            "list student names"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            tables = db.discover_relevant_tables(query)
            print(f"   Discovered tables: {tables}")
            
            # Check if 'students' is in discovered tables
            if 'students' not in tables:
                print(f"   ⚠️ WARNING: 'students' table not discovered!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search():
    """Test if vector search returns student-related results"""
    print("\n" + "="*60)
    print("TEST 5: Vector Search")
    print("="*60)
    
    try:
        vectorstore = VectorStoreService()
        
        query = "how many students are enrolled and their admission numbers"
        results = vectorstore.search(query, k=5)
        
        print(f"Query: '{query}'")
        print(f"Results found: {len(results)}")
        
        for i, result in enumerate(results[:3], 1):
            metadata = result.get('metadata', {})
            score = result.get('score', 0)
            
            print(f"\nResult {i}:")
            print(f"   Type: {metadata.get('type', 'unknown')}")
            print(f"   Entity: {metadata.get('entity', 'unknown')}")
            print(f"   Table: {metadata.get('table_name', 'N/A')}")
            print(f"   Score: {score:.3f}")
            print(f"   Content preview: {result.get('content', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all diagnostic tests"""
    print("\n" + "="*80)
    print("RAG SYSTEM DIAGNOSTICS")
    print("="*80)
    
    results = {
        "Database Connector": test_database_connector(),
        "Query Executor": test_query_executor(),
        "SQL Generation": test_sql_generation(),
        "Table Discovery": test_table_discovery(),
        "Vector Search": test_vector_search()
    }
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - System should work")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()