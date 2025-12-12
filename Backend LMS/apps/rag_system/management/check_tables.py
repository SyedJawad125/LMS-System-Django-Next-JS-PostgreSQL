# # ============================================
# # FIX 3: Management Command to Check Tables
# # File: apps/rag_system/management/commands/check_tables.py
# # ============================================

# from django.core.management.base import BaseCommand
# from apps.rag_system.services.database_connector import DatabaseConnector


# class Command(BaseCommand):
#     help = 'Check database tables for RAG system'

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS('\n📊 Checking Database Tables...\n'))
        
#         db = DatabaseConnector()
        
#         # Get all tables
#         all_tables = db.get_all_tables()
#         self.stdout.write(f"Total tables: {len(all_tables)}\n")
        
#         # Check for teacher tables
#         teacher_tables = [t for t in all_tables if 'teacher' in t.lower()]
#         self.stdout.write(self.style.WARNING(f'\n👨‍🏫 Teacher Tables ({len(teacher_tables)}):'))
#         for table in teacher_tables:
#             self.stdout.write(f"  ✓ {table}")
        
#         # Check for student tables
#         student_tables = [t for t in all_tables if 'student' in t.lower()]
#         self.stdout.write(self.style.WARNING(f'\n👨‍🎓 Student Tables ({len(student_tables)}):'))
#         for table in student_tables:
#             self.stdout.write(f"  ✓ {table}")
        
#         # Check for user tables
#         user_tables = [t for t in all_tables if 'user' in t.lower()]
#         self.stdout.write(self.style.WARNING(f'\n👤 User Tables ({len(user_tables)}):'))
#         for table in user_tables:
#             self.stdout.write(f"  ✓ {table}")
        
#         # Get schema info
#         self.stdout.write(self.style.WARNING('\n\n📋 Getting Schema Info...\n'))
#         schema = db.get_schema_info()
        
#         self.stdout.write(f"\n✅ Schema loaded for {len(schema)} tables:")
#         for table_name in sorted(schema.keys()):
#             columns = len(schema[table_name])
#             self.stdout.write(f"  • {table_name} ({columns} columns)")
        
#         # Test teacher query
#         self.stdout.write(self.style.WARNING('\n\n🧪 Testing Teacher Count Query...\n'))
        
#         if teacher_tables:
#             teacher_table = teacher_tables[0]
#             sql = f"SELECT COUNT(*) as total FROM {teacher_table} WHERE deleted = FALSE OR deleted IS NULL"
#             self.stdout.write(f"SQL: {sql}\n")
            
#             results = db.execute_query(sql)
#             if results:
#                 count = results[0].get('total', 0)
#                 self.stdout.write(self.style.SUCCESS(f"✅ Found {count} teachers in {teacher_table}\n"))
#             else:
#                 self.stdout.write(self.style.ERROR("❌ Query returned no results\n"))
        
#         self.stdout.write(self.style.SUCCESS('\n✅ Check complete!\n'))
