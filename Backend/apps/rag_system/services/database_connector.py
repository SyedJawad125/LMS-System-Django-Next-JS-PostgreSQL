# # ============================================
# # ESSENTIAL DATABASE CONNECTOR FIXES
# # File: apps/rag_system/services/database_connector.py
# # ============================================

# from django.db import connection
# from typing import List, Dict, Optional
# import re


# class DatabaseConnector:
#     """Fixed connector for mixed table naming"""
    
#     def __init__(self):
#         self.connection = connection
#         self._table_mapping = None
    
#     # ADD THIS METHOD - Most important fix
#     def get_actual_table_name(self, entity_type: str, query: str = "") -> Optional[str]:
#         """
#         Get the ACTUAL table name for an entity, handling mixed naming
        
#         Args:
#             entity_type: 'user', 'student', 'teacher', etc.
#             query: Original query for context
            
#         Returns:
#             Actual table name or None
#         """
#         if self._table_mapping is None:
#             self._build_table_mapping()
        
#         entity_lower = entity_type.lower()
        
#         # Direct mapping from your tables
#         direct_map = {
#             # User-related
#             'user': ['users_user', 'users', 'auth_user'],
#             'users': ['users_user', 'users', 'auth_user'],
            
#             # Student-related
#             'student': ['students', 'students_student'],
#             'students': ['students', 'students_student'],
            
#             # Teacher-related
#             'teacher': ['teachers', 'teachers_teacher'],
#             'teachers': ['teachers', 'teachers_teacher'],
            
#             # Role-related
#             'role': ['users_role', 'auth_group'],
#             'roles': ['users_role', 'auth_group'],
            
#             # Parent-related
#             'parent': ['parents'],
#             'parents': ['parents'],
            
#             # Class-related
#             'class': ['classes'],
#             'classes': ['classes'],
            
#             # Subject-related
#             'subject': ['subjects'],
#             'subjects': ['subjects'],
            
#             # Vehicle-related
#             'vehicle': ['vehicles'],
#             'vehicles': ['vehicles'],
            
#             # Route-related
#             'route': ['routes'],
#             'routes': ['routes'],
            
#             # Exam-related
#             'exam': ['exams'],
#             'exams': ['exams'],
            
#             # Fee-related
#             'fee': ['fee_invoices', 'fee_payments'],
#             'fees': ['fee_invoices', 'fee_payments'],
            
#             # Attendance-related
#             'attendance': ['daily_attendance'],
            
#             # Book-related
#             'book': ['images_images'],
#             'books': ['images_images'],
            
#             # Employee-related
#             'employee': ['users_employee'],
#             'employees': ['users_employee'],
            
#             # Permission-related
#             'permission': ['users_permission'],
#             'permissions': ['users_permission'],
#         }
        
#         # Try direct mapping first
#         if entity_lower in direct_map:
#             possible_tables = direct_map[entity_lower]
#             all_tables = self.get_all_tables()
            
#             # Find which table actually exists
#             for table in possible_tables:
#                 if table in all_tables:
#                     print(f"✅ Direct map: '{entity_lower}' → '{table}'")
#                     return table
        
#         # If not found, try to find by pattern
#         return self._find_table_by_pattern(entity_lower, query)
    
#     def _build_table_mapping(self):
#         """Build mapping of entities to actual tables"""
#         all_tables = self.get_all_tables()
#         print(f"📊 Found {len(all_tables)} tables total")
        
#         # Log tables to understand what we have
#         print("Available tables (first 20):")
#         for i, table in enumerate(all_tables[:20]):
#             print(f"  {i+1}. {table}")
        
#         self._table_mapping = all_tables
    
#     def _find_table_by_pattern(self, entity: str, query: str) -> Optional[str]:
#         """Find table by searching patterns"""
#         all_tables = self.get_all_tables()
#         query_lower = query.lower()
        
#         # Pattern matching strategies
#         strategies = [
#             self._strategy_exact_match,
#             self._strategy_contains_entity,
#             self._strategy_related_words,
#             self._strategy_common_prefix,
#         ]
        
#         for strategy in strategies:
#             table = strategy(entity, query_lower, all_tables)
#             if table:
#                 return table
        
#         return None
    
#     def _strategy_exact_match(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
#         """Strategy 1: Exact table name match"""
#         # Check for exact table name
#         if entity in all_tables:
#             return entity
        
#         # Check for plural/singular variations
#         if entity.endswith('s'):
#             singular = entity[:-1]
#             if singular in all_tables:
#                 return singular
#         else:
#             plural = entity + 's'
#             if plural in all_tables:
#                 return plural
        
#         return None
    
#     def _strategy_contains_entity(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
#         """Strategy 2: Table contains entity name"""
#         # Find tables that contain the entity name
#         matching = []
#         for table in all_tables:
#             table_lower = table.lower()
#             if entity in table_lower:
#                 matching.append(table)
        
#         if matching:
#             # Filter out junction tables
#             main_tables = [t for t in matching if not self._is_junction_table(t)]
#             if main_tables:
#                 return main_tables[0]
#             return matching[0]
        
#         return None
    
#     def _strategy_related_words(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
#         """Strategy 3: Use related words from query"""
#         # Map entity types to related keywords
#         related_map = {
#             'user': ['account', 'profile', 'member'],
#             'student': ['pupil', 'learner', 'enrollment'],
#             'teacher': ['instructor', 'faculty', 'staff'],
#             'class': ['grade', 'section', 'course'],
#             'subject': ['discipline', 'topic'],
#             'role': ['position', 'designation'],
#             'parent': ['guardian'],
#             'vehicle': ['bus', 'transport'],
#             'route': ['path', 'journey'],
#             'exam': ['test', 'assessment'],
#             'fee': ['payment', 'invoice'],
#             'attendance': ['presence'],
#             'book': ['publication', 'title', 'library'],
#             'employee': ['staff', 'worker'],
#         }
        
#         if entity in related_map:
#             for keyword in related_map[entity]:
#                 for table in all_tables:
#                     if keyword in table.lower():
#                         return table
        
#         return None
    
#     def _strategy_common_prefix(self, entity: str, query: str, all_tables: List[str]) -> Optional[str]:
#         """Strategy 4: Common Django app prefixes"""
#         # Common Django app prefixes in your system
#         prefixes = ['users_', 'students_', 'teachers_', 'fee_', 'auth_', 'django_']
        
#         for prefix in prefixes:
#             table_name = prefix + entity
#             if table_name in all_tables:
#                 return table_name
        
#         return None
    
#     def _is_junction_table(self, table_name: str) -> bool:
#         """Check if table is a junction/mapping table"""
#         table_lower = table_name.lower()
        
#         # Junction table patterns
#         junction_indicators = [
#             '_to_', '_through_', '_mapping', '_relation',
#             'permission', 'group', 'token', 'history',
#             '_permissions_', '_groups_',
#             'user_role', 'role_permission', 'student_class'
#         ]
        
#         return any(indicator in table_lower for indicator in junction_indicators)
    
#     # UPDATE THIS METHOD for better table discovery
#     def get_best_table_for_query(self, query: str) -> str:
#         """Improved: Find best table for query with mixed naming"""
#         print(f"\n🔍 Finding table for: '{query}'")
        
#         # Extract entity from query
#         entity = self._extract_entity_from_query(query)
        
#         if entity:
#             table = self.get_actual_table_name(entity, query)
#             if table:
#                 print(f"🎯 Found table: {table} (for entity: {entity})")
#                 return table
        
#         # Fallback: Use original logic
#         print("⚠️ Using fallback discovery")
#         return self._fallback_table_discovery(query)
    
#     def _extract_entity_from_query(self, query: str) -> Optional[str]:
#         """Extract main entity from natural language query"""
#         query_lower = query.lower()
        
#         # Remove common question words
#         ignore_words = ['how', 'many', 'count', 'show', 'list', 'get', 
#                        'tell', 'me', 'what', 'are', 'the', 'all', 'of']
        
#         words = query_lower.split()
#         content_words = [w for w in words if w not in ignore_words and len(w) > 2]
        
#         # Common entities in LMS
#         entities = ['user', 'student', 'teacher', 'parent', 'role', 
#                    'class', 'subject', 'vehicle', 'route', 'exam',
#                    'fee', 'attendance', 'book', 'employee']
        
#         # Check for entities
#         for word in content_words:
#             # Direct match
#             if word in entities:
#                 return word
            
#             # Partial match
#             for entity in entities:
#                 if entity in word or word in entity:
#                     return entity
        
#         # Check for plural forms
#         for word in content_words:
#             if word.endswith('s'):
#                 singular = word[:-1]
#                 if singular in entities:
#                     return singular
        
#         return None
    
#     def _fallback_table_discovery(self, query: str) -> Optional[str]:
#         """Original fallback logic"""
#         query_lower = query.lower()
#         all_tables = self.get_all_tables()
        
#         # Common patterns
#         patterns = {
#             'how many users': 'users_user',
#             'how many students': 'students',
#             'how many teachers': 'teachers_teacher',
#             'how many classes': 'classes',
#             'how many roles': 'users_role',
#             'how many vehicles': 'vehicles',
#             'how many routes': 'routes',
#         }
        
#         # Check patterns
#         for pattern, table in patterns.items():
#             if pattern in query_lower and table in all_tables:
#                 return table
        
#         # General search
#         for table in all_tables:
#             table_lower = table.lower()
            
#             # Skip system tables
#             if any(word in table_lower for word in ['token', 'log', 'migration', 'session']):
#                 continue
            
#             # Check if query words match table
#             query_words = query_lower.split()
#             for word in query_words:
#                 if len(word) > 3 and word in table_lower:
#                     if not self._is_junction_table(table):
#                         return table
        
#         return None
    
#     # KEEP ALL YOUR EXISTING METHODS BELOW (get_all_tables, execute_query, etc.)
#     # They should remain unchanged

#     def search_relevant_data(self, query: str, limit: int = 10) -> List[Dict]:
#         """Search across multiple tables for relevant data"""
#         results = []
#         query_lower = query.lower()
        
#         with self.connection.cursor() as cursor:
#             all_tables = self.get_all_tables()
            
#             # Define search mappings
#             search_mappings = {
#                 'teacher': ['teacher', 'teachers', 'faculty', 'staff', 'instructor'],
#                 'student': ['student', 'students', 'pupil', 'learner'],
#                 'route': ['route', 'routes', 'transport'],
#                 'vehicle': ['vehicle', 'vehicles', 'bus', 'buses'],
#                 'fee': ['fee', 'fees', 'payment', 'invoice'],
#                 'exam': ['exam', 'test', 'result', 'marks'],
#                 'attendance': ['attendance', 'absent', 'present'],
#                 'book': ['book', 'books', 'library'],
#                 'class': ['class', 'classes', 'grade'],
#                 'subject': ['subject', 'subjects', 'course'],
#             }
            
#             # Search for each entity type
#             for entity_type, keywords in search_mappings.items():
#                 if any(keyword in query_lower for keyword in keywords):
#                     # Find matching tables
#                     matching_tables = [
#                         t for t in all_tables 
#                         if entity_type in t.lower()
#                     ]
                    
#                     if matching_tables:
#                         print(f"🔍 Found {entity_type} tables: {matching_tables}")
#                         table_name = matching_tables[0]
                        
#                         try:
#                             # Get columns
#                             cursor.execute("""
#                                 SELECT column_name 
#                                 FROM information_schema.columns 
#                                 WHERE table_name = %s
#                                 ORDER BY ordinal_position
#                                 LIMIT 10;
#                             """, [table_name])
                            
#                             columns = [row[0] for row in cursor.fetchall()]
#                             if not columns:
#                                 continue
                            
#                             column_names = ', '.join(columns[:8])
                            
#                             # Build and execute query
#                             sql = f"""
#                                 SELECT {column_names}
#                                 FROM {table_name}
#                                 WHERE (deleted = FALSE OR deleted IS NULL)
#                                 LIMIT %s;
#                             """
                            
#                             table_results = self.execute_query(sql, (limit,))
                            
#                             if table_results:
#                                 results.extend([
#                                     {
#                                         "type": entity_type,
#                                         "table": table_name,
#                                         "data": r
#                                     }
#                                     for r in table_results
#                                 ])
#                                 print(f"✅ Found {len(table_results)} {entity_type} records")
                            
#                         except Exception as e:
#                             print(f"⚠️ Error searching {table_name}: {e}")
#                             continue
        
#         return results

    
#     def _search_table(self, cursor, table_name: str, limit: int, entity_type: str) -> List[Dict]:
#         """Helper method to search a specific table"""
#         try:
#             # Get columns
#             cursor.execute("""
#                 SELECT column_name 
#                 FROM information_schema.columns 
#                 WHERE table_name = %s
#                 ORDER BY ordinal_position
#                 LIMIT 10;
#             """, [table_name])
            
#             columns = [row[0] for row in cursor.fetchall()]
#             if not columns:
#                 return []
            
#             column_names = ', '.join(columns[:8])  # First 8 columns
            
#             # Build SQL with proper WHERE clause
#             sql = f"""
#                 SELECT {column_names}
#                 FROM {table_name}
#                 WHERE (deleted = FALSE OR deleted IS NULL)
#                 LIMIT %s;
#             """
            
#             print(f"🔍 Searching {table_name}...")
#             results = self.execute_query(sql, (limit,))
            
#             return [
#                 {
#                     "type": entity_type, 
#                     "table": table_name, 
#                     "data": r
#                 } 
#                 for r in results
#             ]
            
#         except Exception as e:
#             print(f"⚠️ Error searching {table_name}: {e}")
#             return []
        


#     # Update the discover_relevant_tables method:

#     def discover_relevant_tables(self, query: str) -> List[str]:
#         """Discover which tables are relevant to the query"""
#         all_tables = self.get_all_tables()
#         query_lower = query.lower()
        
#         print(f"📊 All tables in database: {all_tables}")
        
#         # Map keywords to table patterns
#         table_patterns = {
#             'role': ['role', 'roles', 'designation', 'position', 'permission'],
#             'teacher': ['teacher', 'teachers', 'faculty', 'staff'],
#             'student': ['student', 'students', 'pupil'],
#             'class': ['class', 'classes', 'grade', 'section'],
#             'user': ['user', 'users', 'account', 'profile'],
#             'fee': ['fee', 'payment', 'invoice', 'billing'],
#             'exam': ['exam', 'test', 'result', 'marks'],
#             'attendance': ['attendance', 'presence'],
#             'vehicle': ['vehicle', 'vehicles', 'bus', 'transport'],
#             'route': ['route', 'routes', 'journey']
#         }
        
#         relevant_tables = []
        
#         # Check for each keyword
#         for keyword, patterns in table_patterns.items():
#             if any(pattern in query_lower for pattern in patterns):
#                 print(f"🔍 Looking for '{keyword}' related tables...")
                
#                 # Find matching tables
#                 matching_tables = []
#                 for table in all_tables:
#                     table_lower = table.lower()
                    
#                     # Direct match or contains keyword
#                     if any(pattern in table_lower for pattern in patterns):
#                         matching_tables.append(table)
                
#                 if matching_tables:
#                     print(f"✅ Found {keyword} tables: {matching_tables}")
#                     relevant_tables.extend(matching_tables)
        
#         # Also try general search if no specific matches
#         if not relevant_tables:
#             print("⚠️ No specific matches, trying general table search...")
#             for table in all_tables:
#                 table_lower = table.lower()
#                 # Check if table name contains any word from query
#                 query_words = query_lower.split()
#                 if any(word in table_lower for word in query_words if len(word) > 3):
#                     relevant_tables.append(table)
        
#         # Remove duplicates and return
#         unique_tables = list(set(relevant_tables))
#         print(f"🎯 Relevant tables for '{query}': {unique_tables}")
#         return unique_tables

#     def get_table_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
#         """Get sample data from a table to understand its structure"""
#         try:
#             query = f"""
#                 SELECT * 
#                 FROM {table_name} 
#                 WHERE (deleted = FALSE OR deleted IS NULL)
#                 LIMIT %s
#             """
#             return self.execute_query(query, (limit,))
#         except Exception as e:
#             print(f"⚠️ Error getting sample from {table_name}: {e}")
#             return []

#     def get_table_schema_details(self, table_name: str) -> Dict:
#         """Get detailed schema information for a specific table"""
#         try:
#             with self.connection.cursor() as cursor:
#                 # Get columns with details
#                 cursor.execute("""
#                     SELECT 
#                         column_name,
#                         data_type,
#                         is_nullable,
#                         column_default,
#                         character_maximum_length
#                     FROM information_schema.columns 
#                     WHERE table_name = %s
#                     ORDER BY ordinal_position;
#                 """, [table_name])
                
#                 columns = []
#                 for row in cursor.fetchall():
#                     columns.append({
#                         "name": row[0],
#                         "type": row[1],
#                         "nullable": row[2] == 'YES',
#                         "default": row[3],
#                         "max_length": row[4]
#                     })
                
#                 # Get primary key
#                 cursor.execute("""
#                     SELECT kcu.column_name
#                     FROM information_schema.table_constraints tc
#                     JOIN information_schema.key_column_usage kcu
#                     ON tc.constraint_name = kcu.constraint_name
#                     WHERE tc.table_name = %s 
#                     AND tc.constraint_type = 'PRIMARY KEY';
#                 """, [table_name])
                
#                 primary_keys = [row[0] for row in cursor.fetchall()]
                
#                 return {
#                     "table_name": table_name,
#                     "columns": columns,
#                     "primary_keys": primary_keys,
#                     "column_count": len(columns)
#                 }
                
#         except Exception as e:
#             print(f"⚠️ Error getting schema for {table_name}: {e}")
#             return None

#     def smart_schema_extraction(self, query: str) -> Dict:
#         """Extract only relevant schema based on query"""
#         schema = self.get_schema_info()
#         relevant_tables = self.discover_relevant_tables(query)
        
#         filtered_schema = {}
#         for table in relevant_tables:
#             if table in schema:
#                 filtered_schema[table] = schema[table]
        
#         return filtered_schema
    

#     # ADD THESE METHODS TO YOUR EXISTING DatabaseConnector class

#     def analyze_table_content(self, table_name: str) -> Dict:
#         """Analyze what a table actually contains by looking at its data"""
#         try:
#             # Get column info
#             with self.connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT column_name, data_type 
#                     FROM information_schema.columns 
#                     WHERE table_name = %s
#                     ORDER BY ordinal_position;
#                 """, [table_name])
#                 columns = [row[0] for row in cursor.fetchall()]
            
#             # Get sample data to understand content
#             sample_query = f"SELECT * FROM {table_name} LIMIT 3"
#             sample_data = self.execute_query(sample_query)
            
#             # Get row count
#             count_query = f"SELECT COUNT(*) as count FROM {table_name} LIMIT 1"
#             count_result = self.execute_query(count_query)
#             row_count = count_result[0]['count'] if count_result else 0
            
#             # Analyze based on column names and sample data
#             entity_type = self._guess_entity_type(table_name, columns, sample_data)
            
#             return {
#                 "table_name": table_name,
#                 "columns": columns[:10],  # First 10 columns
#                 "row_count": row_count,
#                 "entity_type": entity_type,
#                 "is_main_table": self._is_main_table(table_name, columns),
#                 "has_sample_data": len(sample_data) > 0
#             }
            
#         except Exception as e:
#             print(f"⚠️ Error analyzing {table_name}: {e}")
#             return {"table_name": table_name, "error": str(e)}

#     def _guess_entity_type(self, table_name: str, columns: List[str], sample_data: List[Dict]) -> str:
#         """Intelligently guess what entity this table represents"""
#         table_lower = table_name.lower()
#         columns_lower = [col.lower() for col in columns]
        
#         # Check column patterns
#         column_patterns = {
#             "user": ["username", "email", "password", "first_name", "last_name", "is_active"],
#             "student": ["roll_no", "roll_number", "admission_no", "parent_id", "class_id"],
#             "teacher": ["teacher_id", "qualification", "experience", "designation", "department"],
#             "class": ["class_name", "grade", "section", "class_teacher_id"],
#             "subject": ["subject_name", "subject_code", "credit_hours"],
#             "attendance": ["attendance_date", "status", "present", "absent"],
#             "exam": ["exam_name", "total_marks", "passing_marks", "exam_date"],
#             "fee": ["amount", "due_date", "paid_amount", "balance", "invoice_no"],
#             "book": ["book_title", "author", "isbn", "publisher"],
#             "vehicle": ["vehicle_number", "driver_name", "capacity", "route_id"],
#             "hostel": ["hostel_name", "room_number", "bed_number", "warden_id"],
#             "role": ["role_name", "permissions"],
#             "permission": ["permission_name", "codename", "content_type_id"]
#         }
        
#         # Score each entity type
#         scores = {}
#         for entity, indicators in column_patterns.items():
#             score = 0
            
#             # Column name matches
#             for indicator in indicators:
#                 for column in columns_lower:
#                     if indicator in column:
#                         score += 3
            
#             # Table name matches
#             if entity in table_lower:
#                 score += 5
            
#             # Sample data clues
#             if sample_data:
#                 sample_text = str(sample_data).lower()
#                 for indicator in indicators[:3]:  # First 3 indicators
#                     if indicator in sample_text:
#                         score += 2
            
#             scores[entity] = score
        
#         # Return entity with highest score
#         if scores:
#             best_entity = max(scores.items(), key=lambda x: x[1])
#             if best_entity[1] > 2:  # Minimum confidence
#                 return best_entity[0]
        
#         return "unknown"

#     def _is_main_table(self, table_name: str, columns: List[str]) -> bool:
#         """Check if this is likely a main entity table vs a junction table"""
#         table_lower = table_name.lower()
#         columns_lower = [col.lower() for col in columns]
        
#         # Junction tables often have these patterns
#         junction_indicators = [
#             "id", "created_at", "updated_at", "deleted",  # Only basic columns
#             len(columns) < 5,  # Very few columns
#             any(word in table_lower for word in ["mapping", "junction", "relation", "link"])
#         ]
        
#         # Main tables often have
#         main_table_indicators = [
#             "name", "title", "description",  # Descriptive columns
#             "email", "phone", "address",  # Contact info
#             len(columns) > 8,  # Many columns
#             "date" in table_lower or "log" in table_lower  # Special tables
#         ]
        
#         junction_score = sum(junction_indicators)
#         main_score = sum(main_table_indicators)
        
#         return main_score > junction_score


#     # ADD/UPDATE THESE METHODS:

#     def get_best_table_for_query(self, query: str) -> str:
#         """Smart table discovery for mixed naming conventions"""
#         print(f"🔍 Smart discovery for: '{query}'")
        
#         all_tables = self.get_all_tables()
#         query_lower = query.lower()
        
#         # PHASE 1: Direct keyword-to-table mapping
#         keyword_to_tables = {
#             # User-related
#             'user': ['users_user', 'auth_user'],
#             'users': ['users_user', 'auth_user'],
            
#             # Student-related
#             'student': ['students_student', 'students'],
#             'students': ['students_student', 'students'],
            
#             # Teacher-related
#             'teacher': ['teachers_teacher', 'teachers'],
#             'teachers': ['teachers_teacher', 'teachers'],
            
#             # Role-related
#             'role': ['users_role', 'auth_group'],
#             'roles': ['users_role', 'auth_group'],
            
#             # Parent-related
#             'parent': ['parents'],
#             'parents': ['parents'],
            
#             # Class-related
#             'class': ['classes'],
#             'classes': ['classes'],
            
#             # Subject-related
#             'subject': ['subjects'],
#             'subjects': ['subjects'],
            
#             # Vehicle-related
#             'vehicle': ['vehicles'],
#             'vehicles': ['vehicles'],
            
#             # Route-related
#             'route': ['routes'],
#             'routes': ['routes'],
            
#             # Exam-related
#             'exam': ['exams'],
#             'exams': ['exams'],
            
#             # Fee-related
#             'fee': ['fee_invoices', 'fee_payments'],
#             'fees': ['fee_invoices', 'fee_payments'],
            
#             # Attendance-related
#             'attendance': ['daily_attendance'],
            
#             # Book-related
#             'book': ['images_images'],
#             'books': ['images_images'],
            
#             # Hostel-related (check if exists)
#             'hostel': ['transport_allocations'],  # Might be different
            
#             # Employee-related
#             'employee': ['users_employee'],
#             'employees': ['users_employee'],
#         }
        
#         # Try direct mapping first
#         for keyword, possible_tables in keyword_to_tables.items():
#             if keyword in query_lower:
#                 # Check which tables actually exist
#                 for table in possible_tables:
#                     if table in all_tables:
#                         print(f"✅ Direct map: '{keyword}' → {table}")
#                         return table
        
#         # PHASE 2: Pattern matching for entities
#         entity_to_table_patterns = {
#             'user': ['user$', 'users_'],  # Ends with user or starts with users_
#             'student': ['student$', 'students_'],
#             'teacher': ['teacher$', 'teachers_'],
#             'role': ['role$', '_role'],
#             'class': ['class$', 'classes'],
#             'subject': ['subject$', 'subjects'],
#             'vehicle': ['vehicle$', 'vehicles'],
#             'route': ['route$', 'routes'],
#             'exam': ['exam$', 'exams'],
#             'fee': ['fee_', '_fee'],
#             'attendance': ['attendance'],
#             'parent': ['parent$', 'parents'],
#             'employee': ['employee'],
#         }
        
#         # Extract likely entity from query
#         query_entity = None
#         for entity, patterns in entity_to_table_patterns.items():
#             if entity in query_lower:
#                 query_entity = entity
#                 break
        
#         if query_entity:
#             # Find tables matching the entity
#             matching_tables = []
#             for table in all_tables:
#                 table_lower = table.lower()
                
#                 # Check patterns for this entity
#                 patterns = entity_to_table_patterns.get(query_entity, [])
#                 for pattern in patterns:
#                     import re
#                     if re.search(pattern, table_lower):
#                         matching_tables.append(table)
#                         break
            
#             if matching_tables:
#                 # Prefer tables without underscores for simple names
#                 simple_tables = [t for t in matching_tables if '_' not in t]
#                 if simple_tables:
#                     print(f"✅ Simple table found: {simple_tables[0]}")
#                     return simple_tables[0]
                
#                 # Otherwise use first match
#                 print(f"✅ Pattern match: {matching_tables[0]}")
#                 return matching_tables[0]
        
#         # PHASE 3: Fallback - find any matching table
#         for table in all_tables:
#             table_lower = table.lower()
            
#             # Check if table name contains query words
#             query_words = query_lower.split()
#             for word in query_words:
#                 if len(word) > 3 and word in table_lower:
#                     # Check if it's a main table (not junction table)
#                     if not any(junc in table_lower for junc in ['permission', 'token', 'log', 'history', 'mapping']):
#                         print(f"✅ Fallback match: {table}")
#                         return table
        
#         print("⚠️ No table found")
#         return None

#     def smart_table_discovery(self, query: str) -> Dict:
#         """Smart discovery with multiple strategies"""
#         query_lower = query.lower()
        
#         strategies = [
#             self._strategy_direct_mapping,
#             self._strategy_entity_extraction,
#             self._strategy_pattern_matching,
#             self._strategy_fallback
#         ]
        
#         for strategy in strategies:
#             result = strategy(query_lower)
#             if result:
#                 return result
        
#         return {"table": None, "confidence": 0, "method": "none"}

#     def _strategy_direct_mapping(self, query_lower: str) -> Dict:
#         """Strategy 1: Direct keyword mapping"""
#         direct_map = {
#             'how many users': 'users_user',
#             'how many user': 'users_user',
#             'count users': 'users_user',
            
#             'how many roles': 'users_role',
#             'how many role': 'users_role',
#             'count roles': 'users_role',
            
#             'how many students': 'students_student',
#             'count students': 'students_student',
            
#             'how many teachers': 'teachers_teacher',
#             'count teachers': 'teachers_teacher',
            
#             'how many parents': 'parents',
#             'count parents': 'parents',
            
#             'how many classes': 'classes',
#             'count classes': 'classes',
            
#             'how many vehicles': 'vehicles',
#             'count vehicles': 'vehicles',
            
#             'how many routes': 'routes',
#             'count routes': 'routes',
            
#             'how many employees': 'users_employee',
#             'count employees': 'users_employee',
#         }
        
#         for pattern, table in direct_map.items():
#             if pattern in query_lower:
#                 return {"table": table, "confidence": 0.9, "method": "direct"}
        
#         return None

#     def _strategy_entity_extraction(self, query_lower: str) -> Dict:
#         """Strategy 2: Extract entity and find table"""
#         # Common entity patterns
#         entities = {
#             'user': ['users_user', 'auth_user'],
#             'student': ['students_student', 'students'],
#             'teacher': ['teachers_teacher', 'teachers'],
#             'role': ['users_role', 'auth_group'],
#             'parent': ['parents'],
#             'class': ['classes'],
#             'subject': ['subjects'],
#             'vehicle': ['vehicles'],
#             'route': ['routes'],
#             'exam': ['exams'],
#             'fee': ['fee_invoices'],
#             'attendance': ['daily_attendance'],
#             'employee': ['users_employee'],
#         }
        
#         for entity, tables in entities.items():
#             if entity in query_lower:
#                 all_tables = self.get_all_tables()
#                 for table in tables:
#                     if table in all_tables:
#                         return {"table": table, "confidence": 0.8, "method": "entity"}
        
#         return None

#     def _strategy_pattern_matching(self, query_lower: str) -> Dict:
#         """Strategy 3: Pattern matching in table names"""
#         all_tables = self.get_all_tables()
        
#         # Remove common words
#         ignore_words = ['how', 'many', 'count', 'show', 'list', 'get', 'tell', 'me']
#         query_words = [w for w in query_lower.split() if w not in ignore_words and len(w) > 2]
        
#         for table in all_tables:
#             table_lower = table.lower()
            
#             # Check each query word against table
#             for word in query_words:
#                 # Exact match or contains
#                 if word in table_lower:
#                     # Avoid junction tables
#                     if not any(junc in table_lower for junc in ['permission', 'token', 'log', 'history']):
#                         return {"table": table, "confidence": 0.7, "method": "pattern"}
        
#         return None

#         def _strategy_fallback(self, query_lower: str) -> Dict:
#             """Strategy 4: Fallback to common tables"""
#             common_tables = ['users_user', 'students_student', 'teachers_teacher', 'parents', 'classes', 'vehicles']
            
#             for table in common_tables:
#                 if table in self.get_all_tables():
#                     return {"table": table, "confidence": 0.5, "method": "fallback"}
            
#             return None
        

#         # ADD THESE METHODS TO YOUR EXISTING DatabaseConnector class:

#     def get_all_tables(self) -> List[str]:
#         """Get all tables in database - CRITICAL METHOD THAT'S MISSING"""
#         with self.connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT table_name 
#                 FROM information_schema.tables 
#                 WHERE table_schema = 'public'
#                 AND table_type = 'BASE TABLE'
#                 ORDER BY table_name;
#             """)
#             return [row[0] for row in cursor.fetchall()]

#     def get_table_columns(self, table_name: str) -> List[Dict]:
#         """Get columns for a table"""
#         with self.connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT column_name, data_type, is_nullable
#                 FROM information_schema.columns 
#                 WHERE table_name = %s
#                 ORDER BY ordinal_position;
#             """, [table_name])
            
#             columns = []
#             for row in cursor.fetchall():
#                 columns.append({
#                     "name": row[0],
#                     "type": row[1],
#                     "nullable": row[2] == 'YES'
#                 })
            
#             return columns

#     def analyze_table_content(self, table_name: str) -> Dict:
#         """Simple table analysis"""
#         try:
#             columns = self.get_table_columns(table_name)
#             column_names = [col["name"] for col in columns]
            
#             return {
#                 "table_name": table_name,
#                 "columns": column_names,
#                 "entity_type": self._guess_entity_type_simple(table_name, column_names),
#                 "row_count": 0,  # Simplified for now
#                 "is_main_table": True
#             }
#         except:
#             return {
#                 "table_name": table_name,
#                 "columns": [],
#                 "entity_type": "unknown",
#                 "row_count": 0,
#                 "is_main_table": True
#             }

#     def _guess_entity_type_simple(self, table_name: str, columns: List[str]) -> str:
#         """Simple entity type guess"""
#         table_lower = table_name.lower()
        
#         if "role" in table_lower:
#             return "role"
#         elif "user" in table_lower:
#             return "user"
#         elif "student" in table_lower:
#             return "student"
#         elif "teacher" in table_lower:
#             return "teacher"
#         elif "class" in table_lower:
#             return "class"
#         elif "vehicle" in table_lower:
#             return "vehicle"
#         elif "route" in table_lower:
#             return "route"
#         elif "parent" in table_lower:
#             return "parent"
#         elif "exam" in table_lower:
#             return "exam"
        
#         return "unknown"

#     def get_table_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
#         """Get sample data"""
#         try:
#             return self.execute_query(f"SELECT * FROM {table_name} LIMIT {limit}")
#         except:
#             return []


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