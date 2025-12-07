# ============================================
# QUICK TEST SCRIPT
# Save as: test_rag_now.py in project root
# Run: python test_rag_now.py
# ============================================

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.rag_system.services.database_connector import DatabaseConnector
from apps.rag_system.services.groq_service import GroqService

print("\n" + "="*80)
print("QUICK RAG SYSTEM TEST")
print("="*80)

# Test 1: Check Database Connection
print("\n[Test 1] Checking Database Connection...")
db = DatabaseConnector()
all_tables = db.get_all_tables()
print(f"✅ Found {len(all_tables)} tables")

# Find vehicle tables
vehicle_tables = [t for t in all_tables if 'vehicle' in t.lower()]
print(f"🚗 Vehicle tables: {vehicle_tables}")

route_tables = [t for t in all_tables if 'route' in t.lower()]
print(f"🚌 Route tables: {route_tables}")

# Test 2: Get Schema
print("\n[Test 2] Getting Database Schema...")
schema = db.get_schema_info()
print(f"✅ Schema loaded for {len(schema)} tables")

# Show vehicle/route table schemas
for table in vehicle_tables + route_tables:
    if table in schema:
        cols = [c['name'] for c in schema[table][:5]]
        print(f"  {table}: {', '.join(cols)}")

# Test 3: Generate SQL for Vehicle Query
print("\n[Test 3] Testing SQL Generation...")
groq = GroqService()

test_queries = [
    "Tell me vehicle numbers",
    "Show all vehicles",
    "List transport routes",
    "How many teachers?",
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    sql = groq.generate_sql_query(query, schema)
    if sql:
        print(f"SQL: {sql}")
        
        # Execute it
        results = db.execute_query(sql)
        print(f"Results: {len(results)} rows")
        if results:
            print(f"Sample: {results[0]}")
    else:
        print("❌ SQL generation failed")

# Test 4: Search Function
print("\n[Test 4] Testing search_relevant_data...")
search_results = db.search_relevant_data("vehicle numbers", limit=5)
print(f"Found {len(search_results)} results")
for r in search_results:
    print(f"  Type: {r['type']}, Table: {r['table']}")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)

# Test 5: Full RAG Query
print("\n[Test 5] Testing Full RAG Query...")
from apps.rag_system.services.orchestrator import RAGOrchestrator
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

if user:
    orchestrator = RAGOrchestrator()
    
    result = orchestrator.process_intelligent_query(
        query="Tell me vehicle numbers",
        user_context={
            'user_id': user.id,
            'user_type': 'admin',
            'username': user.username
        }
    )
    
    print(f"\n📊 RAG Query Result:")
    print(f"Query Type: {result.get('query_type')}")
    print(f"Success: {result.get('success')}")
    print(f"SQL Query: {result.get('context_sources', {}).get('sql_query')}")
    print(f"SQL Results: {result.get('context_sources', {}).get('sql_results_count')}")
    print(f"\nResponse:\n{result.get('response')}")
else:
    print("⚠️ No user found for full test")

print("\n" + "="*80)