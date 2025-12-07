# ============================================
# FILE 21: apps/rag_system/management/commands/clear_rag_cache.py
# ============================================

from django.core.management.base import BaseCommand
from apps.rag_system.models import QueryCache, ChatHistory


class Command(BaseCommand):
    help = 'Clear RAG system cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['cache', 'history', 'all'],
            default='cache',
            help='What to clear: cache, history, or all',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Clear entries older than X days',
        )

    def handle(self, *args, **options):
        clear_type = options['type']
        days = options.get('days')
        
        if clear_type in ['cache', 'all']:
            if days:
                from django.utils import timezone
                from datetime import timedelta
                cutoff = timezone.now() - timedelta(days=days)
                count = QueryCache.objects.filter(last_used__lt=cutoff).delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cleared {count} cache entries older than {days} days')
                )
            else:
                count = QueryCache.objects.all().delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cleared all {count} cache entries')
                )
        
        if clear_type in ['history', 'all']:
            if days:
                from django.utils import timezone
                from datetime import timedelta
                cutoff = timezone.now() - timedelta(days=days)
                count = ChatHistory.objects.filter(created_at__lt=cutoff).delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cleared {count} chat history entries older than {days} days')
                )
            else:
                count = ChatHistory.objects.all().delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cleared all {count} chat history entries')
                )