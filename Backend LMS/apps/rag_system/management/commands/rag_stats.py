# ============================================
# FILE 22: apps/rag_system/management/commands/rag_stats.py
# ============================================

from django.core.management.base import BaseCommand
from apps.rag_system.models import (
    DocumentStore, ChatHistory, QueryCache, RAGMetrics
)
from django.db.models import Count, Avg, Sum
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Display RAG system statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n📊 RAG SYSTEM STATISTICS'))
        self.stdout.write('='*60)
        
        # Document Statistics
        self.stdout.write(self.style.WARNING('\n📄 DOCUMENTS:'))
        total_docs = DocumentStore.objects.count()
        processed_docs = DocumentStore.objects.filter(is_processed=True).count()
        pending_docs = total_docs - processed_docs
        
        self.stdout.write(f'  Total Documents: {total_docs}')
        self.stdout.write(f'  Processed: {processed_docs}')
        self.stdout.write(f'  Pending: {pending_docs}')
        
        if total_docs > 0:
            doc_types = DocumentStore.objects.values('document_type').annotate(
                count=Count('id')
            )
            self.stdout.write(f'\n  By Type:')
            for doc_type in doc_types:
                self.stdout.write(f"    - {doc_type['document_type']}: {doc_type['count']}")
        
        # Chat Statistics
        self.stdout.write(self.style.WARNING('\n💬 CHAT HISTORY:'))
        total_chats = ChatHistory.objects.count()
        unique_users = ChatHistory.objects.values('user').distinct().count()
        unique_sessions = ChatHistory.objects.values('session_id').distinct().count()
        
        self.stdout.write(f'  Total Queries: {total_chats}')
        self.stdout.write(f'  Unique Users: {unique_users}')
        self.stdout.write(f'  Unique Sessions: {unique_sessions}')
        
        if total_chats > 0:
            avg_tokens = ChatHistory.objects.aggregate(Avg('tokens_used'))['tokens_used__avg']
            avg_time = ChatHistory.objects.aggregate(Avg('response_time'))['response_time__avg']
            
            self.stdout.write(f'  Avg Tokens/Query: {avg_tokens:.0f}')
            self.stdout.write(f'  Avg Response Time: {avg_time:.2f}s')
        
        # Cache Statistics
        self.stdout.write(self.style.WARNING('\n🗄️ CACHE:'))
        total_cache = QueryCache.objects.count()
        total_hits = QueryCache.objects.aggregate(Sum('hit_count'))['hit_count__sum'] or 0
        
        self.stdout.write(f'  Cached Queries: {total_cache}')
        self.stdout.write(f'  Total Cache Hits: {total_hits}')
        
        if total_cache > 0:
            top_queries = QueryCache.objects.order_by('-hit_count')[:5]
            self.stdout.write(f'\n  Top 5 Cached Queries:')
            for i, query in enumerate(top_queries, 1):
                short_query = query.query_text[:50] + '...' if len(query.query_text) > 50 else query.query_text
                self.stdout.write(f"    {i}. {short_query} (hits: {query.hit_count})")
        
        # Metrics Statistics (Last 7 days)
        self.stdout.write(self.style.WARNING('\n📈 METRICS (Last 7 Days):'))
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        metrics = RAGMetrics.objects.filter(date__gte=seven_days_ago)
        
        if metrics.exists():
            total_queries = metrics.aggregate(Sum('total_queries'))['total_queries__sum']
            successful = metrics.aggregate(Sum('successful_queries'))['successful_queries__sum']
            failed = metrics.aggregate(Sum('failed_queries'))['failed_queries__sum']
            avg_time = metrics.aggregate(Avg('avg_response_time'))['avg_response_time__avg']
            total_tokens = metrics.aggregate(Sum('total_tokens_used'))['total_tokens_used__sum']
            
            success_rate = (successful / total_queries * 100) if total_queries > 0 else 0
            
            self.stdout.write(f'  Total Queries: {total_queries}')
            self.stdout.write(f'  Successful: {successful}')
            self.stdout.write(f'  Failed: {failed}')
            self.stdout.write(f'  Success Rate: {success_rate:.1f}%')
            self.stdout.write(f'  Avg Response Time: {avg_time:.2f}s')
            self.stdout.write(f'  Total Tokens: {total_tokens}')
        else:
            self.stdout.write(f'  No metrics data available')
        
        # Recent Activity
        self.stdout.write(self.style.WARNING('\n🕐 RECENT ACTIVITY:'))
        recent_chats = ChatHistory.objects.order_by('-created_at')[:5]
        
        if recent_chats.exists():
            self.stdout.write(f'  Last 5 Queries:')
            for i, chat in enumerate(recent_chats, 1):
                short_query = chat.query[:50] + '...' if len(chat.query) > 50 else chat.query
                time_ago = datetime.now() - chat.created_at.replace(tzinfo=None)
                minutes_ago = int(time_ago.total_seconds() / 60)
                
                if minutes_ago < 60:
                    time_str = f"{minutes_ago}m ago"
                elif minutes_ago < 1440:
                    time_str = f"{minutes_ago // 60}h ago"
                else:
                    time_str = f"{minutes_ago // 1440}d ago"
                
                self.stdout.write(f"    {i}. {short_query} ({time_str})")
        else:
            self.stdout.write(f'  No recent activity')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✓ Statistics generated successfully!\n'))