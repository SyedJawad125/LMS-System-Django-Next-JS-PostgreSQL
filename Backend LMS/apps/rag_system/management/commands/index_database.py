# ============================================
# FILE 19: apps/rag_system/management/commands/index_database.py
# ============================================

from django.core.management.base import BaseCommand
from apps.rag_system.services.rag_service import RAGService


class Command(BaseCommand):
    help = 'Index database tables into vector store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tables',
            nargs='+',
            type=str,
            help='Specific tables to index',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Index all important tables',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database indexing...'))
        
        try:
            rag_service = RAGService()
            
            if options['tables']:
                tables = options['tables']
                self.stdout.write(f"Indexing specific tables: {', '.join(tables)}")
                rag_service.index_database_tables(tables)
            elif options['all']:
                self.stdout.write("Indexing all important tables...")
                rag_service.index_database_tables(None)
            else:
                # Default tables
                default_tables = [
                    'students', 'teachers', 'classes', 'sections',
                    'subjects', 'attendance', 'exam_results', 'fee_invoices'
                ]
                self.stdout.write(f"Indexing default tables: {', '.join(default_tables)}")
                rag_service.index_database_tables(default_tables)
            
            self.stdout.write(self.style.SUCCESS('✓ Database indexing completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error indexing database: {e}'))
            import traceback
            traceback.print_exc()