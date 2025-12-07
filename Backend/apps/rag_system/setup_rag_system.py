"""
setup_rag_system.py - Complete one-click setup for RAG system
Place this in your project root and run: python setup_rag_system.py
"""

import os
import sys
from pathlib import Path


def main():
    print("\n" + "=" * 80)
    print("LMS RAG SYSTEM - COMPLETE SETUP")
    print("=" * 80)
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Import dependencies
        print("\n[Step 1/5] Importing dependencies...")
        from sqlalchemy.orm import Session
        from apps.database import get_db  # Adjust import based on your structure
        print("✓ Dependencies imported")
        
        # Import our services
        print("\n[Step 2/5] Loading RAG services...")
        from apps.rag_system.services.vectorstore_service import VectorStoreService
        from apps.rag_system.services.schema_extractor import SchemaExtractor
        print("✓ Services loaded")
        
        # Get database connection
        print("\n[Step 3/5] Connecting to database...")
        db = next(get_db())
        print("✓ Database connected")
        
        # Extract schemas
        print("\n[Step 4/5] Extracting all table schemas from PostgreSQL...")
        print("  This will process all 70+ tables automatically...")
        extractor = SchemaExtractor(db)
        schema_docs = extractor.extract_all_schemas()
        print(f"✓ Extracted documentation for {len(schema_docs)} items")
        
        # Initialize vector store
        print("\n[Step 5/5] Populating vector store...")
        vector_store = VectorStoreService(persist_directory="./data/vectorstore")
        vector_store.initialize_from_extractor(schema_docs)
        print("✓ Vector store populated")
        
        # Save backup
        os.makedirs("./data", exist_ok=True)
        extractor.save_to_file(schema_docs, "./data/schema_backup.json")
        
        # Success summary
        print("\n" + "=" * 80)
        print("✓ SETUP COMPLETE!")
        print("=" * 80)
        
        # Statistics
        from collections import Counter
        categories = Counter([doc["metadata"]["category"] for doc in schema_docs])
        
        print("\nSchema Coverage:")
        for category, count in sorted(categories.items()):
            print(f"  • {category.capitalize()}: {count} tables/patterns")
        
        print(f"\nTotal: {len(schema_docs)} schema documents indexed")
        
        print("\n" + "-" * 80)
        print("Your RAG system is ready! Test it with these queries:")
        print("-" * 80)
        print("\n📊 Counting:")
        print("  • How many teachers are there?")
        print("  • Count all students")
        print("  • Total number of classes")
        
        print("\n📋 Listing:")
        print("  • List all teachers")
        print("  • Show students in class 10")
        print("  • Display all active employees")
        
        print("\n🔍 Searching:")
        print("  • Find teachers with more than 5 years experience")
        print("  • Teachers specializing in Mathematics")
        print("  • Students with attendance below 75%")
        
        print("\n📈 Analytics:")
        print("  • What is the average teacher salary?")
        print("  • Which class has the most students?")
        print("  • Total salary expenditure for teachers")
        
        print("\n" + "=" * 80)
        print("API Endpoint: POST /api/rag/chat/query/")
        print("=" * 80)
        
        db.close()
        return True
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nMake sure you have created:")
        print("  1. app/services/schema_extractor.py")
        print("  2. app/services/vector_store.py")
        print("  3. Updated your imports to match your project structure")
        return False
        
    except Exception as e:
        print(f"\n✗ Setup Failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("TROUBLESHOOTING:")
        print("=" * 80)
        print("1. Check database connection in .env file")
        print("2. Ensure PostgreSQL is running")
        print("3. Verify all tables are accessible")
        print("4. Check if you have write permissions for ./data/ folder")
        return False


if __name__ == "__main__":
    # Check for command line options
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("\nClearing existing vector store...")
        import shutil
        if os.path.exists("./data/vectorstore"):
            response = input("Delete existing vector store? (yes/no): ")
            if response.lower() == 'yes':
                shutil.rmtree("./data/vectorstore")
                print("✓ Cleared")
            else:
                print("Cancelled")
                sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)