# ============================================
# FILE 20: apps/rag_system/management/commands/test_rag.py
# ============================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.rag_system.services.orchestrator import RAGOrchestrator


class Command(BaseCommand):
    help = 'Test RAG system with sample queries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            help='Single query to test',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get first user for context
        try:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found in database'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting user: {e}'))
            return
        
        user_context = {
            'user_id': user.id,
            'user_type': getattr(user, 'user_type', 'admin'),
            'username': user.username
        }
        
        # Initialize orchestrator
        self.stdout.write(self.style.SUCCESS('Initializing RAG system...'))
        orchestrator = RAGOrchestrator()
        
        # Test queries
        if options['query']:
            queries = [options['query']]
        else:
            queries = [
                "How many students are enrolled?",
                "Show me all teachers",
                "What is the total fee collection?",
                "List students with pending fees",
                "Calculate average attendance",
            ]
        
        self.stdout.write(self.style.SUCCESS(f'\nTesting {len(queries)} queries:\n'))
        
        for i, query in enumerate(queries, 1):
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(self.style.WARNING(f'Query {i}: {query}'))
            self.stdout.write(f'{"="*60}')
            
            try:
                result = orchestrator.process_intelligent_query(query, user_context)
                
                self.stdout.write(self.style.SUCCESS(f'\n✓ Response:'))
                self.stdout.write(result['response'])
                
                self.stdout.write(f'\n📊 Metrics:')
                self.stdout.write(f'  - Query Type: {result.get("query_type", "N/A")}')
                self.stdout.write(f'  - Tokens Used: {result.get("tokens_used", 0)}')
                self.stdout.write(f'  - Response Time: {result.get("response_time", 0):.2f}s')
                self.stdout.write(f'  - Success: {result.get("success", False)}')
                
                if result.get('context_sources'):
                    self.stdout.write(f'\n📚 Context Sources:')
                    for source, count in result['context_sources'].items():
                        self.stdout.write(f'  - {source}: {count}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n✗ Error: {e}'))
                import traceback
                traceback.print_exc()
        
        self.stdout.write(self.style.SUCCESS(f'\n\n✓ Testing completed!'))