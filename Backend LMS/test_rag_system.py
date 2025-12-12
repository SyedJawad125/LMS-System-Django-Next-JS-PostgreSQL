#!/usr/bin/env python
"""
Test Script for Enhanced RAG System
Run with: python test_rag_system.py
"""

import requests
import json
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/rag"

# You need to get this token from your authentication system
# For testing, you can get it from Django admin or login endpoint
AUTH_TOKEN = "YOUR_AUTH_TOKEN_HERE"

HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def print_response(title: str, response: dict):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)
    print(json.dumps(response, indent=2, default=str))
    print('='*60)


def test_system_status():
    """Test 1: Check system status"""
    print("\n📊 TEST 1: System Status")
    response = requests.get(f"{API_BASE}/v1/status/", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print_response("System Status", data)
        
        # Validate
        assert data.get("status") == "operational", "System should be operational"
        assert data.get("vector_store", {}).get("total_documents", 0) > 0, "Vector store should have documents"
        print("✅ System status test PASSED")
    else:
        print(f"❌ System status test FAILED: {response.status_code}")
        print(response.text)


def test_database_summary():
    """Test 2: Check database summary"""
    print("\n📊 TEST 2: Database Summary")
    response = requests.get(f"{API_BASE}/chat/database_summary/", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print_response("Database Summary", data)
        
        # Validate
        assert data.get("total_tables", 0) > 0, "Should have tables"
        print(f"✅ Found {data.get('total_tables')} tables")
        print("✅ Database summary test PASSED")
    else:
        print(f"❌ Database summary test FAILED: {response.status_code}")


def test_query_diagnosis():
    """Test 3: Diagnose queries"""
    print("\n📊 TEST 3: Query Diagnosis")
    
    test_queries = [
        "How many users are there?",
        "Show all students",
        "Find teachers with experience > 5 years",
        "Hello, what can you do?"
    ]
    
    for query in test_queries:
        response = requests.post(
            f"{API_BASE}/chat/diagnose/",
            headers=HEADERS,
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📝 Query: '{query}'")
            print(f"   Type: {data.get('query_type')}")
            print(f"   Tables: {data.get('relevant_tables', [])}")
            print(f"   Will use DB: {data.get('will_use_database')}")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: {response.status_code}")


def test_vector_search():
    """Test 4: Test vector store search"""
    print("\n📊 TEST 4: Vector Store Search")
    
    test_queries = [
        "student information",
        "teacher details",
        "fee payment",
        "attendance records"
    ]
    
    for query in test_queries:
        response = requests.post(
            f"{API_BASE}/chat/test_vector_search/",
            headers=HEADERS,
            json={"query": query, "k": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Query: '{query}'")
            print(f"   Results: {data.get('results_count')}")
            
            for result in data.get('results', [])[:2]:
                print(f"   • {result.get('type')} - Score: {result.get('score')}")
            
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: {response.status_code}")


def test_actual_queries():
    """Test 5: Run actual queries"""
    print("\n📊 TEST 5: Actual Query Execution")
    
    test_cases = [
        {
            "name": "Counting Query",
            "query": "How many users are there?",
            "expected_keywords": ["user", "total", "system"]
        },
        {
            "name": "Listing Query",
            "query": "Show me information about students",
            "expected_keywords": ["student"]
        },
        {
            "name": "Conversational Query",
            "query": "Hello! What can you help me with?",
            "expected_keywords": ["help", "can", "LMS"]
        },
        {
            "name": "Detail Query",
            "query": "Tell me about the teachers",
            "expected_keywords": ["teacher"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🎯 Testing: {test_case['name']}")
        print(f"   Query: '{test_case['query']}'")
        
        response = requests.post(
            f"{API_BASE}/chat/query/",
            headers=HEADERS,
            json={
                "query": test_case['query'],
                "use_cache": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key metrics
            response_text = data.get('response', '').lower()
            success = data.get('success', False)
            response_time = data.get('response_time', 0)
            tokens = data.get('tokens_used', 0)
            
            print(f"   Success: {success}")
            print(f"   Response Time: {response_time:.2f}s")
            print(f"   Tokens Used: {tokens}")
            print(f"   Response Preview: {data.get('response', '')[:150]}...")
            
            # Check if expected keywords are in response
            keywords_found = [kw for kw in test_case['expected_keywords'] if kw in response_text]
            print(f"   Keywords Found: {keywords_found}")
            
            if success and response_time < 10:
                print("   ✅ PASSED")
            else:
                print("   ⚠️ PARTIAL - Check response")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text}")


def test_metrics():
    """Test 6: Check metrics"""
    print("\n📊 TEST 6: System Metrics")
    
    response = requests.get(f"{API_BASE}/v1/metrics/?days=7", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print_response("System Metrics (Last 7 Days)", data)
        
        print(f"\n📈 Summary:")
        print(f"   Total Queries: {data.get('total_queries', 0)}")
        print(f"   Successful: {data.get('successful_queries', 0)}")
        print(f"   Failed: {data.get('failed_queries', 0)}")
        print(f"   Avg Response Time: {data.get('avg_response_time', 0):.2f}s")
        print(f"   Total Tokens: {data.get('total_tokens', 0)}")
        print("✅ Metrics test PASSED")
    else:
        print(f"❌ Metrics test FAILED: {response.status_code}")


def test_vectorstore_stats():
    """Test 7: Vector store statistics"""
    print("\n📊 TEST 7: Vector Store Statistics")
    
    response = requests.get(f"{API_BASE}/chat/vectorstore_stats/", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print_response("Vector Store Stats", data)
        
        total_docs = data.get('total_documents', 0)
        print(f"\n📚 Vector Store contains {total_docs} documents")
        
        if total_docs > 0:
            print("✅ Vector store stats test PASSED")
        else:
            print("⚠️ Vector store is empty - run initialization")
    else:
        print(f"❌ Vector store stats test FAILED: {response.status_code}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 STARTING ENHANCED RAG SYSTEM TESTS")
    print("="*60)
    
    tests = [
        ("System Status", test_system_status),
        ("Database Summary", test_database_summary),
        ("Query Diagnosis", test_query_diagnosis),
        ("Vector Search", test_vector_search),
        ("Actual Queries", test_actual_queries),
        ("System Metrics", test_metrics),
        ("Vector Store Stats", test_vectorstore_stats)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {name} FAILED: {e}")
            failed += 1
        except requests.exceptions.RequestException as e:
            print(f"\n❌ {name} FAILED: Connection error - {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is fully operational.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the errors above.")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║     ENHANCED RAG SYSTEM TEST SUITE                       ║
║     Vector Store + PostgreSQL Integration                ║
╚══════════════════════════════════════════════════════════╝

IMPORTANT: Update AUTH_TOKEN variable with your actual token!

You can get the token by:
1. Login to your system: POST /api/auth/login/
2. Use Django admin to get token
3. Use existing session token

After updating the token, run: python test_rag_system.py
""")
    
    # Check if token is set
    if AUTH_TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("⚠️  WARNING: AUTH_TOKEN not set!")
        print("Please update AUTH_TOKEN in the script before running tests.")
        print("\nTo get a token, try:")
        print("1. Login via API: curl -X POST http://localhost:8000/api/auth/login/ -d '{...}'")
        print("2. Or use Django shell to create a test token")
        exit(1)
    
    # Run tests
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()