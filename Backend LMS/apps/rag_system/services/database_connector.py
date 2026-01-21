# # ============================================
# # COMPLETELY FIXED DATABASE CONNECTOR
# # MATCHES YOUR ACTUAL POSTGRESQL TABLES
# # File: apps/rag_system/services/database_connector.py
# # ============================================

# from django.db import connection
# from typing import List, Dict, Optional
# import re


# class DatabaseConnector:
#     """Fixed connector with YOUR ACTUAL PostgreSQL table names"""
    
#     def __init__(self):
#         self.connection = connection
#         self._table_mapping = None
#         self._all_tables_cache = None
    
#     def get_all_tables(self) -> List[str]:
#         """Get all tables from PostgreSQL"""
#         if self._all_tables_cache is not None:
#             return self._all_tables_cache
            
#         with self.connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT table_name 
#                 FROM information_schema.tables 
#                 WHERE table_schema = 'public'
#                 AND table_type = 'BASE TABLE'
#                 ORDER BY table_name;
#             """)
#             self._all_tables_cache = [row[0] for row in cursor.fetchall()]
#             return self._all_tables_cache
    
#     def get_actual_table_name(self, entity_type: str, query: str = "") -> Optional[str]:
#         """
#         Get the ACTUAL table name - FIXED FOR YOUR DATABASE
#         """
#         if self._table_mapping is None:
#             self._build_table_mapping()
        
#         entity_lower = entity_type.lower()
#         all_tables = self.get_all_tables()
        
#         # ============================================================
#         # CORRECTED FOR YOUR ACTUAL POSTGRESQL TABLES
#         # Based on images: students, teachers, user, classes, etc.
#         # ============================================================
#         direct_map = {
#             # Student tables
#             'student': ['students'],
#             'students': ['students'],
            
#             # Teacher tables
#             'teacher': ['teachers'],
#             'teachers': ['teachers'],
            
#             # User tables (singular: 'user' not 'users_user')
#             'user': ['user'],
#             'users': ['user'],
            
#             # Parent tables
#             'parent': ['parents'],
#             'parents': ['parents'],
            
#             # Class tables
#             'class': ['classes'],
#             'classes': ['classes'],
            
#             # Subject tables
#             'subject': ['subjects'],
#             'subjects': ['subjects'],
            
#             # Exam tables
#             'exam': ['exams'],
#             'exams': ['exams'],
            
#             # Fee tables
#             'fee': ['fee_invoices'],
#             'fees': ['fee_invoices'],
#             'invoice': ['fee_invoices'],
#             'invoices': ['fee_invoices'],
            
#             # Attendance tables
#             'attendance': ['daily_attendance'],
            
#             # Assignment tables
#             'assignment': ['assignments'],
#             'assignments': ['assignments'],
            
#             # Leave tables
#             'leave': ['leave_applications'],
#             'leaves': ['leave_applications'],
            
#             # Vehicle tables
#             'vehicle': ['vehicles'],
#             'vehicles': ['vehicles'],
            
#             # Route tables
#             'route': ['routes'],
#             'routes': ['routes'],
            
#             # Certificate tables
#             'certificate': ['certificates'],
#             'certificates': ['certificates'],
            
#             # Course tables
#             'course': ['courses'],
#             'courses': ['courses'],
            
#             # Quiz tables
#             'quiz': ['quizzes'],
#             'quizzes': ['quizzes'],
            
#             # Department tables
#             'department': ['departments'],
#             'departments': ['departments'],
            
#             # Message tables (note: 'lnessages' in your DB based on image)
#             'message': ['lnessages', 'messages'],
#             'messages': ['lnessages', 'messages'],
            
#             # Notification tables
#             'notification': ['notifications'],
#             'notifications': ['notifications'],
            
#             # Employee tables
#             'employee': ['employees'],
#             'employees': ['employees'],
            
#             # Role tables
#             'role': ['roles'],
#             'roles': ['roles'],
            
#             # Section tables
#             'section': ['sections'],
#             'sections': ['sections'],
            
#             # Event tables
#             'event': ['events'],
#             'events': ['events'],
            
#             # Permission tables
#             'permission': ['permissions'],
#             'permissions': ['permissions'],
#         }
        
#         # Try direct mapping first
#         if entity_lower in direct_map:
#             possible_tables = direct_map[entity_lower]
            
#             # Find which table actually exists
#             for table in possible_tables:
#                 if table in all_tables:
#                     print(f"✅ Mapped '{entity_lower}' → '{table}'")
#                     return table
        
#         # If not found, try pattern matching
#         return self._find_table_by_pattern(entity_lower, query, all_tables)
    
#     def _build_table_mapping(self):
#         """Build mapping of entities to actual tables"""
#         all_tables = self.get_all_tables()
#         print(f"📊 Found {len(all_tables)} tables in PostgreSQL")
#         self._table_mapping = all_tables
    
#     def _find_table_by_pattern(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
#         """Find table by searching patterns"""
        
#         # Strategy 1: Exact match
#         if entity in all_tables:
#             return entity
        
#         # Strategy 2: Plural/singular variations
#         if entity.endswith('s'):
#             singular = entity[:-1]
#             if singular in all_tables:
#                 return singular
#         else:
#             plural = entity + 's'
#             if plural in all_tables:
#                 return plural
        
#         # Strategy 3: Contains entity name
#         matching = []
#         for table in all_tables:
#             table_lower = table.lower()
#             if entity in table_lower:
#                 matching.append(table)
        
#         if matching:
#             matching.sort(key=len)
#             main_tables = [t for t in matching if not self._is_junction_table(t)]
#             if main_tables:
#                 return main_tables[0]
#             return matching[0]
        
#         print(f"⚠️ WARNING: Could not find table for entity '{entity}'")
#         return None
    
#     def _is_junction_table(self, table_name: str) -> bool:
#         """Check if table is a junction/mapping table"""
#         table_lower = table_name.lower()
        
#         junction_indicators = [
#             '_permissions', '_groups', 'permission', 'token',
#             'blacklist', '_log', 'migration', 'session', 'admin',
#             '_workflow', '_emailtemplate', '_target_', 'django_'
#         ]
        
#         return any(indicator in table_lower for indicator in junction_indicators)
    
#     def get_table_columns(self, table_name: str) -> List[Dict]:
#         """Get columns for a table"""
#         with self.connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     column_name, 
#                     data_type, 
#                     is_nullable,
#                     column_default
#                 FROM information_schema.columns 
#                 WHERE table_name = %s
#                 ORDER BY ordinal_position;
#             """, [table_name])
            
#             columns = []
#             for row in cursor.fetchall():
#                 columns.append({
#                     "name": row[0],
#                     "type": row[1],
#                     "nullable": row[2] == 'YES',
#                     "default": row[3]
#                 })
            
#             return columns
    
#     def get_table_schema_info(self, table_name: str) -> Dict:
#         """Get comprehensive schema information"""
#         try:
#             columns = self.get_table_columns(table_name)
#             column_names = [col["name"] for col in columns]
            
#             # Get row count
#             with self.connection.cursor() as cursor:
#                 # Check if table has 'deleted' column
#                 has_deleted = 'deleted' in column_names
                
#                 if has_deleted:
#                     cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE (deleted = FALSE OR deleted IS NULL)")
#                 else:
#                     cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    
#                 row_count = cursor.fetchone()[0]
            
#             return {
#                 "table_name": table_name,
#                 "columns": column_names,
#                 "column_details": columns,
#                 "row_count": row_count,
#                 "entity_type": self._guess_entity_type(table_name, column_names),
#                 "has_deleted_field": has_deleted
#             }
#         except Exception as e:
#             print(f"⚠️ Error getting schema for {table_name}: {e}")
#             return {
#                 "table_name": table_name,
#                 "columns": [],
#                 "error": str(e)
#             }
    
#     def _guess_entity_type(self, table_name: str, columns: List[str]) -> str:
#         """Guess entity type from table name"""
#         table_lower = table_name.lower()
        
#         entity_patterns = {
#             "student": ["student"],
#             "teacher": ["teacher"],
#             "user": ["user"],
#             "parent": ["parent"],
#             "role": ["role"],
#             "class": ["class"],
#             "subject": ["subject"],
#             "exam": ["exam"],
#             "fee": ["fee", "invoice", "payment"],
#             "attendance": ["attendance"],
#             "vehicle": ["vehicle"],
#             "route": ["route"],
#             "employee": ["employee"],
#             "assignment": ["assignment"],
#             "leave": ["leave"],
#             "department": ["department"],
#             "quiz": ["quiz"],
#             "certificate": ["certificate"],
#             "course": ["course"],
#             "section": ["section"],
#             "event": ["event"],
#             "message": ["message", "lnessage"],  # Note: lnessages in your DB
#             "notification": ["notification"]
#         }
        
#         for entity, keywords in entity_patterns.items():
#             for keyword in keywords:
#                 if keyword in table_lower:
#                     return entity
        
#         return "unknown"
    
#     def execute_query(self, sql: str, params: tuple = None) -> List[Dict]:
#         """Execute SQL query with SMART safety check"""
#         try:
#             # --- START SMART SAFETY CHECK ---
#             sql_upper = sql.upper()
            
#             # This regex \b ensures we only block the standalone word 'DELETE'
#             # It will NOT block 'deleted', '"deleted"', or 'is_deleted'
#             import re
#             if re.search(r'\bDELETE\b', sql_upper):
#                 print(f"🛑 Security Block: Standalone DELETE command detected!")
#                 # We return an empty list so the system doesn't crash but knows it was blocked
#                 return [] 
#             # --- END SMART SAFETY CHECK ---

#             with self.connection.cursor() as cursor:
#                 cursor.execute(sql, params)
                
#                 # If no description, it was likely an illegal write operation
#                 if not cursor.description:
#                     return []

#                 columns = [col[0] for col in cursor.description]
#                 results = []
#                 for row in cursor.fetchall():
#                     row_dict = {}
#                     for col_name, value in zip(columns, row):
#                         row_dict[col_name] = value if value is not None else None
#                     results.append(row_dict)
                
#                 return results
#         except Exception as e:
#             print(f"❌ Query execution error: {e}")
#             return []
    
#     def get_schema_info(self) -> Dict:
#         """Get schema information for all tables"""
#         all_tables = self.get_all_tables()
#         schema = {}
        
#         # Filter out system tables
#         user_tables = [t for t in all_tables if not any(
#             skip in t.lower() for skip in [
#                 'django_', 'auth_permission', 'auth_group_permissions',
#                 'token_blacklist', 'celery'
#             ]
#         )]
        
#         for table in user_tables:
#             schema[table] = self.get_table_schema_info(table)
        
#         return schema
    
#     def discover_relevant_tables(self, query: str) -> List[str]:
#         """Discover which tables are relevant to the query"""
#         all_tables = self.get_all_tables()
#         query_lower = query.lower()
        
#         # Map keywords to entity types
#         keyword_map = {
#             'user': ['user', 'account', 'profile'],
#             'student': ['student', 'pupil', 'learner'],
#             'teacher': ['teacher', 'instructor', 'faculty'],
#             'parent': ['parent', 'guardian'],
#             'class': ['class', 'grade', 'section'],
#             'subject': ['subject', 'course'],
#             'exam': ['exam', 'test', 'assessment', 'result'],
#             'fee': ['fee', 'payment', 'invoice', 'billing'],
#             'attendance': ['attendance', 'present', 'absent'],
#             'vehicle': ['vehicle', 'bus', 'transport'],
#             'route': ['route', 'path'],
#             'assignment': ['assignment', 'homework', 'submission'],
#             'leave': ['leave', 'absence', 'vacation'],
#             'employee': ['employee', 'staff', 'worker'],
#             'department': ['department', 'division'],
#             'quiz': ['quiz', 'question'],
#             'certificate': ['certificate', 'credential'],
#             'message': ['message', 'notification', 'announcement'],
#             'event': ['event', 'activity'],
#         }
        
#         relevant_tables = []
        
#         # Find relevant entity types
#         for entity, keywords in keyword_map.items():
#             if any(keyword in query_lower for keyword in keywords):
#                 # Find matching tables
#                 table_name = self.get_actual_table_name(entity, query)
#                 if table_name and table_name not in relevant_tables:
#                     relevant_tables.append(table_name)
        
#         # If no specific matches, search broadly
#         if not relevant_tables:
#             query_words = [w for w in query_lower.split() if len(w) > 3]
#             for table in all_tables:
#                 table_lower = table.lower()
#                 if any(word in table_lower for word in query_words):
#                     if not self._is_junction_table(table):
#                         relevant_tables.append(table)
        
#         print(f"🎯 Relevant tables for '{query}': {relevant_tables}")
#         return relevant_tables[:5]  # Limit to top 5 tables



# ============================================
# FINAL FIXED DATABASE CONNECTOR  
# File: apps/rag_system/services/database_connector.py
# ============================================

from django.db import connection
from typing import List, Dict, Optional


class DatabaseConnector:
    """Fixed connector - won't block 'deleted' column"""
    
    def __init__(self):
        self.connection = connection
        self._table_mapping = None
        self._all_tables_cache = None
    
    def get_all_tables(self) -> List[str]:
        """Get all tables from PostgreSQL"""
        if self._all_tables_cache is not None:
            return self._all_tables_cache
            
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            self._all_tables_cache = [row[0] for row in cursor.fetchall()]
            return self._all_tables_cache
    
    def get_actual_table_name(self, entity_type: str, query: str = "") -> Optional[str]:
        """Get actual table name for entity"""
        if self._table_mapping is None:
            self._build_table_mapping()
        
        entity_lower = entity_type.lower()
        all_tables = self.get_all_tables()
        
        # Mappings based on YOUR actual PostgreSQL tables
        direct_map = {
            'student': ['students'], 'students': ['students'],
            'teacher': ['teachers'], 'teachers': ['teachers'],
            'user': ['user'], 'users': ['user'],
            'parent': ['parents'], 'parents': ['parents'],
            'class': ['classes'], 'classes': ['classes'],
            'subject': ['subjects'], 'subjects': ['subjects'],
            'exam': ['exams'], 'exams': ['exams'],
            'fee': ['fee_invoices'], 'fees': ['fee_invoices'],
            'attendance': ['daily_attendance'],
            'assignment': ['assignments'], 'assignments': ['assignments'],
            'leave': ['leave_applications'], 'leaves': ['leave_applications'],
            'vehicle': ['vehicles'], 'vehicles': ['vehicles'],
            'route': ['routes'], 'routes': ['routes'],
            'certificate': ['certificates'], 'certificates': ['certificates'],
            'course': ['courses'], 'courses': ['courses'],
            'quiz': ['quizzes'], 'quizzes': ['quizzes'],
            'department': ['departments'], 'departments': ['departments'],
            'message': ['lnessages', 'messages'], 'messages': ['lnessages', 'messages'],
            'notification': ['notifications'], 'notifications': ['notifications'],
            'employee': ['employees'], 'employees': ['employees'],
            'role': ['roles'], 'roles': ['roles'],
            'section': ['sections'], 'sections': ['sections'],
            'event': ['events'], 'events': ['events'],
            'permission': ['permissions'], 'permissions': ['permissions'],
        }
        
        if entity_lower in direct_map:
            for table in direct_map[entity_lower]:
                if table in all_tables:
                    print(f"✅ Mapped '{entity_lower}' → '{table}'")
                    return table
        
        return self._find_table_by_pattern(entity_lower, query, all_tables)
    
    def _build_table_mapping(self):
        """Build table mapping"""
        all_tables = self.get_all_tables()
        print(f"📊 Found {len(all_tables)} tables")
        self._table_mapping = all_tables
    
    def _find_table_by_pattern(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
        """Find table by pattern"""
        if entity in all_tables:
            return entity
        
        if entity.endswith('s'):
            singular = entity[:-1]
            if singular in all_tables:
                return singular
        else:
            plural = entity + 's'
            if plural in all_tables:
                return plural
        
        matching = [t for t in all_tables if entity in t.lower()]
        if matching:
            matching.sort(key=len)
            main = [t for t in matching if not self._is_junction_table(t)]
            return main[0] if main else matching[0]
        
        return None
    
    def _is_junction_table(self, table_name: str) -> bool:
        """Check if junction table"""
        indicators = ['_permissions', '_groups', 'token', 'blacklist', 'django_', 'migration']
        return any(ind in table_name.lower() for ind in indicators)
    
    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Get columns for table"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
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
                    "default": row[3]
                })
            return columns
    
    def get_table_schema_info(self, table_name: str) -> Dict:
        """Get schema info"""
        try:
            columns = self.get_table_columns(table_name)
            column_names = [col["name"] for col in columns]
            
            with self.connection.cursor() as cursor:
                has_deleted = 'deleted' in column_names
                
                if has_deleted:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE deleted = false")
                else:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    
                row_count = cursor.fetchone()[0]
            
            return {
                "table_name": table_name,
                "columns": column_names,
                "column_details": columns,
                "row_count": row_count,
                "entity_type": self._guess_entity_type(table_name),
                "has_deleted_field": has_deleted
            }
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return {"table_name": table_name, "columns": [], "error": str(e)}
    
    def _guess_entity_type(self, table_name: str) -> str:
        """Guess entity type"""
        patterns = {
            "student": ["student"], "teacher": ["teacher"], "user": ["user"],
            "parent": ["parent"], "class": ["class"], "subject": ["subject"],
            "exam": ["exam"], "fee": ["fee", "invoice"], "attendance": ["attendance"],
            "vehicle": ["vehicle"], "route": ["route"], "employee": ["employee"],
            "assignment": ["assignment"], "leave": ["leave"], "department": ["department"],
            "quiz": ["quiz"], "certificate": ["certificate"], "course": ["course"],
            "section": ["section"], "event": ["event"], "message": ["message", "lnessage"],
            "notification": ["notification"]
        }
        
        table_lower = table_name.lower()
        for entity, keywords in patterns.items():
            if any(kw in table_lower for kw in keywords):
                return entity
        return "unknown"
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict]:
        """
        Execute SQL - NO BLOCKING OF 'deleted' COLUMN
        
        Security is handled in query_executor.py, not here
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if not cursor.description:
                    return []
                
                columns = [col[0] for col in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    row_dict = {}
                    for col_name, value in zip(columns, row):
                        row_dict[col_name] = value
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            print(f"❌ Query error: {e}")
            return []
    
    def discover_relevant_tables(self, query: str) -> List[str]:
        """Discover relevant tables"""
        all_tables = self.get_all_tables()
        query_lower = query.lower()
        
        keyword_map = {
            'user': ['user', 'account'], 'student': ['student', 'pupil'],
            'teacher': ['teacher', 'instructor'], 'parent': ['parent', 'guardian'],
            'class': ['class', 'grade'], 'subject': ['subject'],
            'exam': ['exam', 'test'], 'fee': ['fee', 'payment', 'invoice'],
            'attendance': ['attendance'], 'vehicle': ['vehicle', 'bus'],
            'route': ['route'], 'assignment': ['assignment', 'homework'],
            'leave': ['leave'], 'employee': ['employee', 'staff'],
            'department': ['department'], 'quiz': ['quiz'],
            'certificate': ['certificate'], 'message': ['message']
        }
        
        relevant = []
        for entity, keywords in keyword_map.items():
            if any(kw in query_lower for kw in keywords):
                table = self.get_actual_table_name(entity, query)
                if table and table not in relevant:
                    relevant.append(table)
        
        if not relevant:
            words = [w for w in query_lower.split() if len(w) > 3]
            for table in all_tables:
                if any(w in table.lower() for w in words):
                    if not self._is_junction_table(table):
                        relevant.append(table)
        
        print(f"🎯 Relevant tables: {relevant}")
        return relevant[:5]