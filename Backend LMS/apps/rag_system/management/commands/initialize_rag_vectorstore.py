# # apps/rag_system/management/commands/initialize_rag_vectorstore.py
# """
# Django management command to initialize RAG vector store

# Usage:
#     python manage.py initialize_rag_vectorstore
#     python manage.py initialize_rag_vectorstore --refresh
#     python manage.py initialize_rag_vectorstore --test
# """

# from django.core.management.base import BaseCommand
# from apps.rag_system.services.vectorstore_service import VectorStoreService
# from apps.rag_system.services.database_connector import DatabaseConnector


# class Command(BaseCommand):
#     help = 'Initialize RAG vector store with PostgreSQL data'
    
#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--refresh',
#             action='store_true',
#             help='Force refresh - rebuild all embeddings',
#         )
#         parser.add_argument(
#             '--test',
#             action='store_true',
#             help='Run test queries after initialization',
#         )
    
#     def handle(self, *args, **options):
#         refresh = options['refresh']
#         test = options['test']
        
#         self.stdout.write("="*70)
#         self.stdout.write(self.style.SUCCESS('RAG VECTOR STORE INITIALIZATION'))
#         self.stdout.write("="*70)
        
#         # Initialize services
#         self.stdout.write("\n📦 Initializing services...")
#         vectorstore = VectorStoreService()
#         db_connector = DatabaseConnector()
        
#         # Show current state
#         stats = vectorstore.stats()
#         self.stdout.write(f"   Current documents: {stats.get('total_documents', 0)}")
        
#         if stats.get('total_documents', 0) > 0 and not refresh:
#             self.stdout.write(self.style.WARNING(
#                 "\n⚠️  Vector store already initialized!"
#             ))
#             self.stdout.write("   Use --refresh to rebuild")
            
#             if not test:
#                 return
        
#         # Initialize
#         if stats.get('total_documents', 0) == 0 or refresh:
#             self.stdout.write("\n💾 Injecting PostgreSQL data into vector store...")
#             self.stdout.write("   This may take 1-2 minutes...")
            
#             try:
#                 vectorstore.initialize_with_database_knowledge(refresh=refresh)
                
#                 new_stats = vectorstore.stats()
#                 self.stdout.write(self.style.SUCCESS(
#                     f"\n✅ Success! Created {new_stats.get('total_documents', 0)} embeddings"
#                 ))
                
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f"\n❌ Error: {e}"))
#                 import traceback
#                 traceback.print_exc()
#                 return
        
#         # Test if requested
#         if test:
#             self.stdout.write("\n🧪 Running test queries...")
            
#             test_queries = [
#                 ('students', 'Testing student entity search'),
#                 ('teachers', 'Testing teacher entity search'),
#                 ('how many users', 'Testing counting query'),
#                 ('exam', 'Testing exam-related search'),
#                 ('fee payment', 'Testing fee-related search'),
#             ]
            
#             for query, description in test_queries:
#                 self.stdout.write(f"\n   {description}")
#                 self.stdout.write(f"   Query: '{query}'")
                
#                 try:
#                     results = vectorstore.search(query, k=3)
                    
#                     if results:
#                         top = results[0]
#                         metadata = top.get('metadata', {})
                        
#                         self.stdout.write(self.style.SUCCESS(
#                             f"   ✅ Found {len(results)} results"
#                         ))
#                         self.stdout.write(
#                             f"      Top: {metadata.get('type', 'unknown')} "
#                             f"(entity: {metadata.get('entity', 'N/A')}, "
#                             f"score: {top.get('score', 0):.3f})"
#                         )
#                     else:
#                         self.stdout.write(self.style.WARNING(
#                             "   ⚠️  No results found"
#                         ))
                        
#                 except Exception as e:
#                     self.stdout.write(self.style.ERROR(f"   ❌ Error: {e}"))
        
#         # Summary
#         self.stdout.write("\n" + "="*70)
#         self.stdout.write(self.style.SUCCESS('✅ INITIALIZATION COMPLETE'))
#         self.stdout.write("="*70)
        
#         self.stdout.write("\nNext steps:")
#         self.stdout.write("  1. Test via API: POST /api/rag/chat/query/")
#         self.stdout.write("  2. Check stats: GET /api/rag/chat/vectorstore_stats/")
#         self.stdout.write("  3. View docs: GET /api/rag/chat/database_summary/")