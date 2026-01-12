# ============================================
# ENHANCED DATABASE CONNECTOR
# File: apps/rag_system/services/database_connector.py
# ============================================

from django.db import connection
from typing import List, Dict, Optional
import re


class DatabaseConnector:
    """Enhanced connector for mixed table naming with PostgreSQL"""
    
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
        """
        Get the ACTUAL table name for an entity, handling mixed naming
        
        Args:
            entity_type: 'user', 'student', 'teacher', etc.
            query: Original query for context
            
        Returns:
            Actual table name or None
        """
        if self._table_mapping is None:
            self._build_table_mapping()
        
        entity_lower = entity_type.lower()
        all_tables = self.get_all_tables()
        
        # Direct mapping based on your actual tables
        direct_map = {
            # User-related
            'user': ['users_user', 'auth_user'],
            'users': ['users_user', 'auth_user'],
            
            # Student-related
            'student': ['students', 'student_behavior', 'student_discounts'],
            'students': ['students', 'student_behavior', 'student_discounts'],
            
            # Teacher-related
            'teacher': ['teachers', 'teachers_teacher'],
            'teachers': ['teachers', 'teachers_teacher'],
            
            # Role-related
            'role': ['users_role', 'users_role_permissions', 'auth_group'],
            'roles': ['users_role', 'users_role_permissions', 'auth_group'],
            
            # Parent-related
            'parent': ['parents', 'parents_students'],
            'parents': ['parents', 'parents_students'],
            
            # Class-related
            'class': ['classes', 'class_subjects'],
            'classes': ['classes', 'class_subjects'],
            
            # Subject-related
            'subject': ['subjects', 'class_subjects'],
            'subjects': ['subjects', 'class_subjects'],
            
            # Vehicle-related
            'vehicle': ['vehicles'],
            'vehicles': ['vehicles'],
            
            # Route-related
            'route': ['routes'],
            'routes': ['routes'],
            
            # Exam-related
            'exam': ['exams', 'exam_results', 'exam_schedules', 'exam_types'],
            'exams': ['exams', 'exam_results', 'exam_schedules', 'exam_types'],
            
            # Fee-related
            'fee': ['fee_invoices', 'fee_payments', 'fee_structures', 'fee_types'],
            'fees': ['fee_invoices', 'fee_payments', 'fee_structures', 'fee_types'],
            
            # Attendance-related
            'attendance': ['daily_attendance', 'attendance_summary', 'attendance_configuration'],
            
            # Book/Library-related
            'book': ['images_images', 'images_categories'],
            'books': ['images_images', 'images_categories'],
            
            # Employee-related
            'employee': ['users_employee'],
            'employees': ['users_employee'],
            
            # Permission-related
            'permission': ['users_permission', 'auth_permission'],
            'permissions': ['users_permission', 'auth_permission'],
            
            # Assignment-related
            'assignment': ['assignments', 'assignment_submissions'],
            'assignments': ['assignments', 'assignment_submissions'],
            
            # Leave-related
            'leave': ['leave_applications', 'leave_balances', 'leave_types'],
            'leaves': ['leave_applications', 'leave_balances', 'leave_types'],
            
            # Message-related
            'message': ['messages'],
            'messages': ['messages'],
            
            # Notification-related
            'notification': ['notifications'],
            'notifications': ['notifications'],
            
            # Department-related
            'department': ['departments'],
            'departments': ['departments'],
            
            # Course-related
            'course': ['courses', 'course_enrollments'],
            'courses': ['courses', 'course_enrollments'],
            
            # Quiz-related
            'quiz': ['quizzes', 'quiz_answers', 'quiz_attempts'],
            'quizzes': ['quizzes', 'quiz_answers', 'quiz_attempts'],
            
            # Timetable-related
            'timetable': ['timetables', 'time_slots'],
            'timetables': ['timetables', 'time_slots'],
            
            # Certificate-related
            'certificate': ['certificates', 'certificate_templates'],
            'certificates': ['certificates', 'certificate_templates'],
        }
        
        # Try direct mapping first
        if entity_lower in direct_map:
            possible_tables = direct_map[entity_lower]
            
            # Find which table actually exists
            for table in possible_tables:
                if table in all_tables:
                    print(f"✅ Direct map: '{entity_lower}' → '{table}'")
                    return table
        
        # If not found, try pattern matching
        return self._find_table_by_pattern(entity_lower, query, all_tables)
    
    def _build_table_mapping(self):
        """Build mapping of entities to actual tables"""
        all_tables = self.get_all_tables()
        print(f"📊 Found {len(all_tables)} tables in PostgreSQL")
        
        # Log tables for debugging
        print("📋 Available tables (sample):")
        for i, table in enumerate(all_tables[:30]):
            print(f"  {i+1}. {table}")
        
        self._table_mapping = all_tables
    
    def _find_table_by_pattern(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
        """Find table by searching patterns"""
        query_lower = query.lower()
        
        # Strategy 1: Exact match
        if entity in all_tables:
            return entity
        
        # Strategy 2: Plural/singular variations
        if entity.endswith('s'):
            singular = entity[:-1]
            if singular in all_tables:
                return singular
        else:
            plural = entity + 's'
            if plural in all_tables:
                return plural
        
        # Strategy 3: Contains entity name
        matching = []
        for table in all_tables:
            table_lower = table.lower()
            if entity in table_lower:
                matching.append(table)
        
        if matching:
            # Filter out junction/mapping tables
            main_tables = [t for t in matching if not self._is_junction_table(t)]
            if main_tables:
                return main_tables[0]
            return matching[0]
        
        # Strategy 4: Common prefixes
        prefixes = ['users_', 'auth_', 'django_', 'rag_']
        for prefix in prefixes:
            table_name = prefix + entity
            if table_name in all_tables:
                return table_name
        
        return None
    
    def _is_junction_table(self, table_name: str) -> bool:
        """Check if table is a junction/mapping table"""
        table_lower = table_name.lower()
        
        junction_indicators = [
            '_permissions', '_groups_', 'permission', 'token',
            'blacklist', 'log', 'migration', 'session', 'admin'
        ]
        
        return any(indicator in table_lower for indicator in junction_indicators)
    
    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Get columns for a table"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
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
        """Get comprehensive schema information"""
        try:
            columns = self.get_table_columns(table_name)
            column_names = [col["name"] for col in columns]
            
            # Get row count
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
            
            return {
                "table_name": table_name,
                "columns": column_names,
                "column_details": columns,
                "row_count": row_count,
                "entity_type": self._guess_entity_type(table_name, column_names)
            }
        except Exception as e:
            print(f"⚠️ Error getting schema for {table_name}: {e}")
            return {
                "table_name": table_name,
                "columns": [],
                "error": str(e)
            }
    
    def _guess_entity_type(self, table_name: str, columns: List[str]) -> str:
        """Guess entity type from table name and columns"""
        table_lower = table_name.lower()
        
        entity_patterns = {
            "user": ["user", "account"],
            "student": ["student", "pupil"],
            "teacher": ["teacher", "instructor"],
            "role": ["role", "permission"],
            "class": ["class", "grade", "section"],
            "subject": ["subject", "course"],
            "exam": ["exam", "test", "result"],
            "fee": ["fee", "payment", "invoice"],
            "attendance": ["attendance"],
            "vehicle": ["vehicle", "transport"],
            "route": ["route"],
            "parent": ["parent", "guardian"],
            "employee": ["employee", "staff"],
            "assignment": ["assignment"],
            "leave": ["leave"],
            "department": ["department"],
            "quiz": ["quiz"],
            "certificate": ["certificate"]
        }
        
        for entity, keywords in entity_patterns.items():
            for keyword in keywords:
                if keyword in table_lower:
                    return entity
        
        return "unknown"
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict]:
        """Execute SQL query and return results as list of dicts"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                # Get column names
                columns = [col[0] for col in cursor.description]
                
                # Fetch results
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            print(f"   SQL: {sql}")
            return []
    
    def get_schema_info(self) -> Dict:
        """Get schema information for all tables"""
        all_tables = self.get_all_tables()
        schema = {}
        
        for table in all_tables:
            # Skip system tables
            if any(skip in table.lower() for skip in ['django_', 'auth_permission', 'token_blacklist']):
                continue
            
            schema[table] = self.get_table_schema_info(table)
        
        return schema
    
    def discover_relevant_tables(self, query: str) -> List[str]:
        """Discover which tables are relevant to the query"""
        all_tables = self.get_all_tables()
        query_lower = query.lower()
        
        # Map keywords to entity types
        keyword_map = {
            'user': ['user', 'account', 'profile', 'auth'],
            'student': ['student', 'pupil', 'learner'],
            'teacher': ['teacher', 'instructor', 'faculty', 'staff'],
            'parent': ['parent', 'guardian'],
            'class': ['class', 'grade', 'section'],
            'subject': ['subject', 'course', 'discipline'],
            'exam': ['exam', 'test', 'assessment', 'result'],
            'fee': ['fee', 'payment', 'invoice', 'billing'],
            'attendance': ['attendance', 'present', 'absent'],
            'vehicle': ['vehicle', 'bus', 'transport'],
            'route': ['route', 'path'],
            'assignment': ['assignment', 'homework', 'submission'],
            'leave': ['leave', 'absence', 'vacation'],
            'employee': ['employee', 'staff', 'worker'],
            'department': ['department', 'division'],
            'quiz': ['quiz', 'test', 'question'],
            'certificate': ['certificate', 'credential'],
            'timetable': ['timetable', 'schedule', 'time_slot'],
            'message': ['message', 'notification', 'announcement'],
        }
        
        relevant_tables = []
        
        # Find relevant entity types
        for entity, keywords in keyword_map.items():
            if any(keyword in query_lower for keyword in keywords):
                # Find matching tables
                table_name = self.get_actual_table_name(entity, query)
                if table_name and table_name not in relevant_tables:
                    relevant_tables.append(table_name)
        
        # If no specific matches, search broadly
        if not relevant_tables:
            query_words = [w for w in query_lower.split() if len(w) > 3]
            for table in all_tables:
                table_lower = table.lower()
                if any(word in table_lower for word in query_words):
                    if not self._is_junction_table(table):
                        relevant_tables.append(table)
        
        print(f"🎯 Relevant tables for '{query}': {relevant_tables}")
        return relevant_tables[:5]  # Limit to top 5 tables