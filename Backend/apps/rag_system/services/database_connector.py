# # ============================================
# # FIX 1: Update Database Connector
# # File: apps/rag_system/services/database_connector.py
# # ============================================

# from django.db import connection
# from typing import List, Dict
# import json


# class DatabaseConnector:
#     """Connect to PostgreSQL and execute queries"""
    
#     def __init__(self):
#         self.connection = connection
#         # Cache schema info for performance
#         self._schema_cache = None
    
#     def get_all_tables(self) -> List[str]:
#         """Get all tables in database"""
#         with self.connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT table_name 
#                 FROM information_schema.tables 
#                 WHERE table_schema = 'public'
#                 AND table_type = 'BASE TABLE'
#                 ORDER BY table_name;
#             """)
#             return [row[0] for row in cursor.fetchall()]
    
#     def get_schema_info(self) -> Dict:
#         """Get database schema information for LLM"""
#         # Return cached schema if available
#         if self._schema_cache:
#             return self._schema_cache
        
#         schema = {}
#         all_tables = self.get_all_tables()
        
#         print(f"\n📊 Found {len(all_tables)} total tables in database")
        
#         # Priority tables - check these first
#         priority_keywords = [
#             'teacher', 'student', 'user', 'employee',
#             'class', 'subject', 'fee', 'attendance', 
#             'exam', 'grade', 'result', 'invoice'
#         ]
        
#         # Get priority tables
#         priority_tables = [
#             table for table in all_tables 
#             if any(keyword in table.lower() for keyword in priority_keywords)
#         ]
        
#         print(f"📌 Priority LMS tables: {priority_tables[:20]}")
        
#         # Get schema for priority tables
#         with self.connection.cursor() as cursor:
#             for table in priority_tables[:25]:  # Limit to 25 tables
#                 try:
#                     cursor.execute("""
#                         SELECT column_name, data_type, is_nullable
#                         FROM information_schema.columns 
#                         WHERE table_name = %s
#                         ORDER BY ordinal_position;
#                     """, [table])
                    
#                     columns = [
#                         {
#                             "name": row[0], 
#                             "type": row[1],
#                             "nullable": row[2] == 'YES'
#                         } 
#                         for row in cursor.fetchall()
#                     ]
                    
#                     if columns:
#                         schema[table] = columns
                        
#                 except Exception as e:
#                     print(f"⚠️ Error getting schema for {table}: {e}")
#                     continue
        
#         # Cache the schema
#         self._schema_cache = schema
#         print(f"✅ Loaded schema for {len(schema)} tables\n")
        
#         return schema
    
#     def execute_query(self, sql_query: str, params: tuple = None) -> List[Dict]:
#         """Execute SQL query and return results"""
#         try:
#             with self.connection.cursor() as cursor:
#                 if params:
#                     cursor.execute(sql_query, params)
#                 else:
#                     cursor.execute(sql_query)
                
#                 columns = [col[0] for col in cursor.description] if cursor.description else []
#                 results = []
                
#                 for row in cursor.fetchall():
#                     row_dict = {}
#                     for col, val in zip(columns, row):
#                         # Handle datetime/date objects
#                         if val is not None and hasattr(val, 'isoformat'):
#                             row_dict[col] = val.isoformat()
#                         else:
#                             row_dict[col] = val
#                     results.append(row_dict)
                
#                 print(f"✅ Query returned {len(results)} rows")
#                 return results
                
#         except Exception as e:
#             print(f"❌ Database query error: {e}")
#             print(f"Query was: {sql_query}")
#             return []
    
#     def search_relevant_data(self, query: str, limit: int = 10) -> List[Dict]:
#         """Search across multiple tables for relevant data"""
#         results = []
#         query_lower = query.lower()
        
#         with self.connection.cursor() as cursor:
#             # Get all available tables
#             all_tables = self.get_all_tables()
            
#             # Search for TEACHERS
#             if any(word in query_lower for word in ['teacher', 'teachers', 'faculty', 'staff', 'instructor']):
#                 # Find teacher-related tables
#                 teacher_tables = [t for t in all_tables if 'teacher' in t.lower()]
#                 print(f"🔍 Found teacher tables: {teacher_tables}")
                
#                 if teacher_tables:
#                     # Use the first teacher table found
#                     teacher_table = teacher_tables[0]
                    
#                     # Get columns for this table
#                     cursor.execute("""
#                         SELECT column_name 
#                         FROM information_schema.columns 
#                         WHERE table_name = %s
#                         ORDER BY ordinal_position
#                         LIMIT 10;
#                     """, [teacher_table])
                    
#                     columns = [row[0] for row in cursor.fetchall()]
#                     column_names = ', '.join(columns[:5])  # First 5 columns
                    
#                     sql = f"""
#                         SELECT {column_names}
#                         FROM {teacher_table}
#                         WHERE deleted = FALSE OR deleted IS NULL
#                         LIMIT %s;
#                     """
                    
#                     teachers = self.execute_query(sql, (limit,))
#                     if teachers:
#                         results.extend([{"type": "teacher", "table": teacher_table, "data": t} for t in teachers])
            
#             # Search for STUDENTS
#             elif any(word in query_lower for word in ['student', 'students', 'pupil', 'learner']):
#                 student_tables = [t for t in all_tables if 'student' in t.lower()]
#                 print(f"🔍 Found student tables: {student_tables}")
                
#                 if student_tables:
#                     student_table = student_tables[0]
                    
#                     cursor.execute("""
#                         SELECT column_name 
#                         FROM information_schema.columns 
#                         WHERE table_name = %s
#                         ORDER BY ordinal_position
#                         LIMIT 10;
#                     """, [student_table])
                    
#                     columns = [row[0] for row in cursor.fetchall()]
#                     column_names = ', '.join(columns[:5])
                    
#                     sql = f"""
#                         SELECT {column_names}
#                         FROM {student_table}
#                         WHERE deleted = FALSE OR deleted IS NULL
#                         LIMIT %s;
#                     """
                    
#                     students = self.execute_query(sql, (limit,))
#                     if students:
#                         results.extend([{"type": "student", "table": student_table, "data": s} for s in students])
        
#         return results




# # ============================================
# # FIX 4: Quick Test Script
# # Save as: test_teacher_query.py in project root
# # ============================================

# """
# from django.core.management import execute_from_command_line
# import os
# import sys

# # Add project to path
# sys.path.insert(0, os.path.dirname(__file__))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# import django
# django.setup()

# from apps.rag_system.services.database_connector import DatabaseConnector
# from apps.rag_system.services.groq_service import GroqService

# print("=" * 60)
# print("Testing Teacher Query")
# print("=" * 60)

# # 1. Check tables
# db = DatabaseConnector()
# all_tables = db.get_all_tables()
# teacher_tables = [t for t in all_tables if 'teacher' in t.lower()]

# print(f"\\n1. Found teacher tables: {teacher_tables}")

# # 2. Get schema
# schema = db.get_schema_info()
# print(f"\\n2. Schema loaded for {len(schema)} tables")

# # 3. Test SQL generation
# groq = GroqService()
# sql = groq.generate_sql_query("How many teachers?", schema)
# print(f"\\n3. Generated SQL: {sql}")

# # 4. Execute query
# if sql:
#     results = db.execute_query(sql)
#     print(f"\\n4. Query results: {results}")

# print("\\n" + "=" * 60)
# """



# ============================================
# UPDATED DATABASE CONNECTOR
# File: apps/rag_system/services/database_connector.py
# ============================================

from django.db import connection
from typing import List, Dict
import json


class DatabaseConnector:
    """Connect to PostgreSQL and execute queries"""
    
    def __init__(self):
        self.connection = connection
        self._schema_cache = None
    
    def get_all_tables(self) -> List[str]:
        """Get all tables in database"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            return [row[0] for row in cursor.fetchall()]
    
    def get_schema_info(self) -> Dict:
        """Get database schema information for LLM"""
        if self._schema_cache:
            return self._schema_cache
        
        schema = {}
        all_tables = self.get_all_tables()
        
        print(f"\n📊 Found {len(all_tables)} total tables in database")
        
        # Priority keywords for LMS tables
        priority_keywords = [
            'teacher', 'student', 'user', 'employee',
            'class', 'subject', 'section', 'grade',
            'fee', 'payment', 'invoice', 'attendance', 
            'exam', 'result', 'mark', 'score',
            'route', 'transport', 'vehicle', 'bus',
            'book', 'library', 'hostel', 'room',
            'assignment', 'homework', 'timetable'
        ]
        
        # Get priority tables
        priority_tables = [
            table for table in all_tables 
            if any(keyword in table.lower() for keyword in priority_keywords)
        ]
        
        print(f"📌 Priority LMS tables found: {len(priority_tables)}")
        
        # Get schema for priority tables
        with self.connection.cursor() as cursor:
            for table in priority_tables[:30]:  # Increased limit
                try:
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = %s
                        ORDER BY ordinal_position;
                    """, [table])
                    
                    columns = [
                        {
                            "name": row[0], 
                            "type": row[1],
                            "nullable": row[2] == 'YES'
                        } 
                        for row in cursor.fetchall()
                    ]
                    
                    if columns:
                        schema[table] = columns
                        
                except Exception as e:
                    print(f"⚠️ Error getting schema for {table}: {e}")
                    continue
        
        self._schema_cache = schema
        print(f"✅ Loaded schema for {len(schema)} tables\n")
        
        return schema
    
    def execute_query(self, sql_query: str, params: tuple = None) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(sql_query, params)
                else:
                    cursor.execute(sql_query)
                
                columns = [col[0] for col in cursor.description] if cursor.description else []
                results = []
                
                for row in cursor.fetchall():
                    row_dict = {}
                    for col, val in zip(columns, row):
                        if val is not None and hasattr(val, 'isoformat'):
                            row_dict[col] = val.isoformat()
                        else:
                            row_dict[col] = val
                    results.append(row_dict)
                
                print(f"✅ Query returned {len(results)} rows")
                return results
                
        except Exception as e:
            print(f"❌ Database query error: {e}")
            print(f"Query was: {sql_query}")
            return []
    
    # def search_relevant_data(self, query: str, limit: int = 10) -> List[Dict]:
    #     """Search across multiple tables for relevant data"""
    #     results = []
    #     query_lower = query.lower()
        
    #     with self.connection.cursor() as cursor:
    #         all_tables = self.get_all_tables()
            
    #         # ✅ EXPANDED SEARCH LOGIC
            
    #         # 1. TEACHERS
    #         if any(word in query_lower for word in ['teacher', 'teachers', 'faculty', 'staff', 'instructor']):
    #             teacher_tables = [t for t in all_tables if 'teacher' in t.lower()]
    #             if teacher_tables:
    #                 results.extend(self._search_table(cursor, teacher_tables[0], limit, 'teacher'))
            
    #         # 2. STUDENTS
    #         if any(word in query_lower for word in ['student', 'students', 'pupil', 'learner']):
    #             student_tables = [t for t in all_tables if 'student' in t.lower()]
    #             if student_tables:
    #                 results.extend(self._search_table(cursor, student_tables[0], limit, 'student'))
            
    #         # 3. ROUTES / TRANSPORT ✅ NEW
    #         if any(word in query_lower for word in ['route', 'routes', 'transport', 'bus', 'vehicle']):
    #             route_tables = [t for t in all_tables if 'route' in t.lower() or 'transport' in t.lower()]
    #             print(f"🚌 Found route tables: {route_tables}")
    #             if route_tables:
    #                 results.extend(self._search_table(cursor, route_tables[0], limit, 'route'))
            
    #         # 4. FEES
    #         if any(word in query_lower for word in ['fee', 'fees', 'payment', 'invoice']):
    #             fee_tables = [t for t in all_tables if 'fee' in t.lower() or 'payment' in t.lower() or 'invoice' in t.lower()]
    #             if fee_tables:
    #                 results.extend(self._search_table(cursor, fee_tables[0], limit, 'fee'))
            
    #         # 5. EXAMS
    #         if any(word in query_lower for word in ['exam', 'test', 'result', 'marks']):
    #             exam_tables = [t for t in all_tables if 'exam' in t.lower() or 'result' in t.lower()]
    #             if exam_tables:
    #                 results.extend(self._search_table(cursor, exam_tables[0], limit, 'exam'))
            
    #         # 6. ATTENDANCE
    #         if any(word in query_lower for word in ['attendance', 'absent', 'present']):
    #             attendance_tables = [t for t in all_tables if 'attendance' in t.lower()]
    #             if attendance_tables:
    #                 results.extend(self._search_table(cursor, attendance_tables[0], limit, 'attendance'))
            
    #         # 7. LIBRARY / BOOKS
    #         if any(word in query_lower for word in ['book', 'books', 'library']):
    #             book_tables = [t for t in all_tables if 'book' in t.lower() or 'library' in t.lower()]
    #             if book_tables:
    #                 results.extend(self._search_table(cursor, book_tables[0], limit, 'book'))
        
    #     return results

    def search_relevant_data(self, query: str, limit: int = 10) -> List[Dict]:
        """Search across multiple tables for relevant data"""
        results = []
        query_lower = query.lower()
        
        with self.connection.cursor() as cursor:
            all_tables = self.get_all_tables()
            
            # Define search mappings
            search_mappings = {
                'teacher': ['teacher', 'teachers', 'faculty', 'staff', 'instructor'],
                'student': ['student', 'students', 'pupil', 'learner'],
                'route': ['route', 'routes', 'transport'],
                'vehicle': ['vehicle', 'vehicles', 'bus', 'buses'],
                'fee': ['fee', 'fees', 'payment', 'invoice'],
                'exam': ['exam', 'test', 'result', 'marks'],
                'attendance': ['attendance', 'absent', 'present'],
                'book': ['book', 'books', 'library'],
                'class': ['class', 'classes', 'grade'],
                'subject': ['subject', 'subjects', 'course'],
            }
            
            # Search for each entity type
            for entity_type, keywords in search_mappings.items():
                if any(keyword in query_lower for keyword in keywords):
                    # Find matching tables
                    matching_tables = [
                        t for t in all_tables 
                        if entity_type in t.lower()
                    ]
                    
                    if matching_tables:
                        print(f"🔍 Found {entity_type} tables: {matching_tables}")
                        table_name = matching_tables[0]
                        
                        try:
                            # Get columns
                            cursor.execute("""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name = %s
                                ORDER BY ordinal_position
                                LIMIT 10;
                            """, [table_name])
                            
                            columns = [row[0] for row in cursor.fetchall()]
                            if not columns:
                                continue
                            
                            column_names = ', '.join(columns[:8])
                            
                            # Build and execute query
                            sql = f"""
                                SELECT {column_names}
                                FROM {table_name}
                                WHERE (deleted = FALSE OR deleted IS NULL)
                                LIMIT %s;
                            """
                            
                            table_results = self.execute_query(sql, (limit,))
                            
                            if table_results:
                                results.extend([
                                    {
                                        "type": entity_type,
                                        "table": table_name,
                                        "data": r
                                    }
                                    for r in table_results
                                ])
                                print(f"✅ Found {len(table_results)} {entity_type} records")
                            
                        except Exception as e:
                            print(f"⚠️ Error searching {table_name}: {e}")
                            continue
        
        return results

    
    def _search_table(self, cursor, table_name: str, limit: int, entity_type: str) -> List[Dict]:
        """Helper method to search a specific table"""
        try:
            # Get columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
                LIMIT 10;
            """, [table_name])
            
            columns = [row[0] for row in cursor.fetchall()]
            if not columns:
                return []
            
            column_names = ', '.join(columns[:8])  # First 8 columns
            
            # Build SQL with proper WHERE clause
            sql = f"""
                SELECT {column_names}
                FROM {table_name}
                WHERE (deleted = FALSE OR deleted IS NULL)
                LIMIT %s;
            """
            
            print(f"🔍 Searching {table_name}...")
            results = self.execute_query(sql, (limit,))
            
            return [
                {
                    "type": entity_type, 
                    "table": table_name, 
                    "data": r
                } 
                for r in results
            ]
            
        except Exception as e:
            print(f"⚠️ Error searching {table_name}: {e}")
            return []
        


    # Update the discover_relevant_tables method:

    def discover_relevant_tables(self, query: str) -> List[str]:
        """Discover which tables are relevant to the query"""
        all_tables = self.get_all_tables()
        query_lower = query.lower()
        
        print(f"📊 All tables in database: {all_tables}")
        
        # Map keywords to table patterns
        table_patterns = {
            'role': ['role', 'roles', 'designation', 'position', 'permission'],
            'teacher': ['teacher', 'teachers', 'faculty', 'staff'],
            'student': ['student', 'students', 'pupil'],
            'class': ['class', 'classes', 'grade', 'section'],
            'user': ['user', 'users', 'account', 'profile'],
            'fee': ['fee', 'payment', 'invoice', 'billing'],
            'exam': ['exam', 'test', 'result', 'marks'],
            'attendance': ['attendance', 'presence'],
            'vehicle': ['vehicle', 'vehicles', 'bus', 'transport'],
            'route': ['route', 'routes', 'journey']
        }
        
        relevant_tables = []
        
        # Check for each keyword
        for keyword, patterns in table_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                print(f"🔍 Looking for '{keyword}' related tables...")
                
                # Find matching tables
                matching_tables = []
                for table in all_tables:
                    table_lower = table.lower()
                    
                    # Direct match or contains keyword
                    if any(pattern in table_lower for pattern in patterns):
                        matching_tables.append(table)
                
                if matching_tables:
                    print(f"✅ Found {keyword} tables: {matching_tables}")
                    relevant_tables.extend(matching_tables)
        
        # Also try general search if no specific matches
        if not relevant_tables:
            print("⚠️ No specific matches, trying general table search...")
            for table in all_tables:
                table_lower = table.lower()
                # Check if table name contains any word from query
                query_words = query_lower.split()
                if any(word in table_lower for word in query_words if len(word) > 3):
                    relevant_tables.append(table)
        
        # Remove duplicates and return
        unique_tables = list(set(relevant_tables))
        print(f"🎯 Relevant tables for '{query}': {unique_tables}")
        return unique_tables

    def get_table_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample data from a table to understand its structure"""
        try:
            query = f"""
                SELECT * 
                FROM {table_name} 
                WHERE (deleted = FALSE OR deleted IS NULL)
                LIMIT %s
            """
            return self.execute_query(query, (limit,))
        except Exception as e:
            print(f"⚠️ Error getting sample from {table_name}: {e}")
            return []

    def get_table_schema_details(self, table_name: str) -> Dict:
        """Get detailed schema information for a specific table"""
        try:
            with self.connection.cursor() as cursor:
                # Get columns with details
                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, [table_name])
                
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == 'YES',
                        "default": row[3],
                        "max_length": row[4]
                    })
                
                # Get primary key
                cursor.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = %s 
                    AND tc.constraint_type = 'PRIMARY KEY';
                """, [table_name])
                
                primary_keys = [row[0] for row in cursor.fetchall()]
                
                return {
                    "table_name": table_name,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "column_count": len(columns)
                }
                
        except Exception as e:
            print(f"⚠️ Error getting schema for {table_name}: {e}")
            return None

    def smart_schema_extraction(self, query: str) -> Dict:
        """Extract only relevant schema based on query"""
        schema = self.get_schema_info()
        relevant_tables = self.discover_relevant_tables(query)
        
        filtered_schema = {}
        for table in relevant_tables:
            if table in schema:
                filtered_schema[table] = schema[table]
        
        return filtered_schema