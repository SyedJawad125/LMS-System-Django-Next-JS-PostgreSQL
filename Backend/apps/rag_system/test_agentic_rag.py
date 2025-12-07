# NEW FILE - Test the system

from services.rag_service import RAGService
import time

def test_role_query():
    """Test the 'how many roles' query"""
    print("🧪 Testing Agentic RAG System")
    print("=" * 60)
    
    # Initialize service
    rag = RAGService()
    
    # Test query
    query = "please tell me how many roles"
    print(f"📝 Query: {query}")
    
    # Process query
    start = time.time()
    result = rag.process_query(query, use_cache=False)
    elapsed = time.time() - start
    
    print("\n📊 RESULTS:")
    print(f"✅ Success: {result['success']}")
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"🔍 Query Type: {result.get('query_type', 'unknown')}")
    
    print("\n🗂️ Context Sources:")
    sources = result.get('context_sources', {})
    print(f"  • SQL Query: {sources.get('sql_query', 'None')}")
    print(f"  • SQL Results: {sources.get('sql_results_count', 0)}")
    print(f"  • Vector Store: {sources.get('vector_store', 0)}")
    print(f"  • Tables Attempted: {sources.get('tables_attempted', [])}")
    
    print("\n🤖 Response:")
    print(result.get('response', 'No response'))
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_role_query()