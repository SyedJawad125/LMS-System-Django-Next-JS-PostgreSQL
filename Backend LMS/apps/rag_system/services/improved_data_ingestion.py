# ============================================
# IMPROVED DATA INGESTION SERVICE
# File: apps/rag_system/services/data_ingestion.py
# ============================================

"""
This service creates RICH, CONTEXTUAL embeddings from your PostgreSQL database.
Key improvements:
1. Semantic descriptions of data relationships
2. Example queries with expected results
3. Business logic documentation
4. Column value examples and patterns
"""

from typing import List, Dict, Tuple
from django.db import connection
import json


class ImprovedDataIngestion:
    """Creates rich, contextual knowledge base from PostgreSQL"""
    
    def __init__(self):
        self.connection = connection
        
    def generate_rich_knowledge_base(self) -> List[Dict]:
        """Generate comprehensive knowledge documents"""
        
        documents = []
        
        # 1. Entity-centric documents (with relationships)
        documents.extend(self._create_entity_documents())
        
        # 2. Query pattern documents (with examples)
        documents.extend(self._create_query_pattern_documents())
        
        # 3. Business logic documents
        documents.extend(self._create_business_logic_documents())
        
        # 4. Column semantics documents
        documents.extend(self._create_column_semantic_documents())
        
        # 5. Relationship mapping documents
        documents.extend(self._create_relationship_documents())
        
        return documents
    
    def _create_entity_documents(self) -> List[Dict]:
        """Create rich entity-centric documents"""
        
        # Define your main entities with their context
        entities = {
            'student': {
                'tables': ['students', 'student_behavior', 'student_profiles'],
                'description': 'Students are learners enrolled in the institution',
                'common_queries': [
                    'How many students are enrolled?',
                    'List students by class',
                    'Show student attendance records',
                    'Find students with low attendance'
                ],
                'relationships': {
                    'classes': 'Students are enrolled in classes',
                    'attendance': 'Students have daily attendance records',
                    'exams': 'Students take exams and get results',
                    'parents': 'Students have parent/guardian relationships'
                }
            },
            'teacher': {
                'tables': ['teachers', 'teacher_profiles'],
                'description': 'Teachers are educators who teach subjects and manage classes',
                'common_queries': [
                    'How many teachers are employed?',
                    'List teachers by department',
                    'Show teacher schedules',
                    'Find teachers teaching specific subjects'
                ],
                'relationships': {
                    'classes': 'Teachers are assigned to teach classes',
                    'subjects': 'Teachers specialize in specific subjects',
                    'departments': 'Teachers belong to academic departments'
                }
            },
            'user': {
                'tables': ['users_user', 'auth_user'],
                'description': 'Users are system accounts with roles and permissions',
                'common_queries': [
                    'How many users are registered?',
                    'List users by role',
                    'Show active users',
                    'Find users with specific permissions'
                ],
                'relationships': {
                    'roles': 'Users are assigned roles that determine permissions',
                    'permissions': 'Users have specific access rights'
                }
            },
            'class': {
                'tables': ['classes', 'class_subjects'],
                'description': 'Classes are groups of students learning together',
                'common_queries': [
                    'How many classes exist?',
                    'List classes by grade level',
                    'Show class schedules',
                    'Find classes with specific subjects'
                ],
                'relationships': {
                    'students': 'Classes contain enrolled students',
                    'teachers': 'Classes are taught by assigned teachers',
                    'subjects': 'Classes cover multiple subjects'
                }
            },
            'exam': {
                'tables': ['exams', 'exam_results', 'exam_schedules'],
                'description': 'Exams are assessments to evaluate student performance',
                'common_queries': [
                    'How many exams are scheduled?',
                    'List exam results',
                    'Show upcoming exams',
                    'Find students who failed exams'
                ],
                'relationships': {
                    'students': 'Students take exams and receive grades',
                    'subjects': 'Exams are conducted for specific subjects',
                    'classes': 'Exams are scheduled for classes'
                }
            },
            'attendance': {
                'tables': ['daily_attendance', 'attendance_summary'],
                'description': 'Attendance tracks student presence in classes',
                'common_queries': [
                    'What is the attendance rate?',
                    'List absent students today',
                    'Show attendance trends',
                    'Find students with low attendance'
                ],
                'relationships': {
                    'students': 'Attendance records belong to students',
                    'classes': 'Attendance is tracked per class'
                }
            },
            'fee': {
                'tables': ['fee_invoices', 'fee_payments', 'fee_structures'],
                'description': 'Fees are charges for educational services',
                'common_queries': [
                    'How much fees collected?',
                    'List pending fee invoices',
                    'Show payment history',
                    'Find students with outstanding fees'
                ],
                'relationships': {
                    'students': 'Fees are charged to students',
                    'payments': 'Invoices can have multiple payments'
                }
            }
        }
        
        documents = []
        
        for entity_name, entity_info in entities.items():
            # Get actual table schema
            main_table = self._get_best_table(entity_info['tables'])
            
            if not main_table:
                continue
                
            schema = self._get_detailed_schema(main_table)
            sample_data = self._get_sample_data(main_table, limit=3)
            row_count = self._get_row_count(main_table)
            
            # Create comprehensive document
            content = f"""
ENTITY: {entity_name.upper()}
{'=' * 80}

DESCRIPTION:
{entity_info['description']}

DATABASE TABLES:
Primary: {main_table}
Related: {', '.join([t for t in entity_info['tables'] if t != main_table])}
Total Records: {row_count:,}

SCHEMA DETAILS:
{self._format_schema(schema)}

COMMON QUERY PATTERNS:
{self._format_queries(entity_info['common_queries'])}

RELATIONSHIPS:
{self._format_relationships(entity_info['relationships'])}

SQL EXAMPLES:

1. Count total {entity_name}s:
   SELECT COUNT(*) as total 
   FROM {main_table} 
   WHERE deleted = false
   Expected Result: Single row with 'total' column showing count

2. List all {entity_name}s:
   SELECT * 
   FROM {main_table} 
   WHERE deleted = false 
   LIMIT 100
   Expected Result: Up to 100 rows with all columns

3. Search {entity_name}s by name (if name column exists):
   SELECT * 
   FROM {main_table} 
   WHERE deleted = false 
   AND name ILIKE '%search_term%'
   LIMIT 50
   Expected Result: Matching records with name containing search term

SAMPLE DATA STRUCTURE:
{self._format_sample_data(sample_data)}

IMPORTANT NOTES:
- Always filter by 'deleted = false' to get active records only
- Use ILIKE for case-insensitive text search in PostgreSQL
- Current record count: {row_count:,} active {entity_name}s
- Primary key: {schema.get('primary_key', 'id')}
"""
            
            documents.append({
                'content': content.strip(),
                'metadata': {
                    'type': 'entity_knowledge',
                    'entity': entity_name,
                    'table': main_table,
                    'record_count': row_count,
                    'priority': 'very_high',  # Entity docs are most important
                    'keywords': self._extract_keywords(entity_name, entity_info)
                }
            })
        
        return documents
    
    def _create_query_pattern_documents(self) -> List[Dict]:
        """Create query pattern documents with real examples"""
        
        patterns = [
            {
                'pattern': 'COUNT',
                'description': 'Queries asking for total number of records',
                'triggers': ['how many', 'count', 'total', 'number of'],
                'examples': [
                    {
                        'query': 'How many students are there?',
                        'sql': 'SELECT COUNT(*) as total FROM students WHERE deleted = false',
                        'expected': 'Single number result'
                    },
                    {
                        'query': 'Total number of teachers?',
                        'sql': 'SELECT COUNT(*) as total FROM teachers WHERE deleted = false',
                        'expected': 'Count of active teachers'
                    }
                ]
            },
            {
                'pattern': 'LIST',
                'description': 'Queries requesting list of records',
                'triggers': ['list', 'show', 'display', 'get all'],
                'examples': [
                    {
                        'query': 'List all students',
                        'sql': 'SELECT * FROM students WHERE deleted = false LIMIT 100',
                        'expected': 'Multiple rows with student details'
                    },
                    {
                        'query': 'Show active users',
                        'sql': 'SELECT * FROM users_user WHERE deleted = false AND is_active = true LIMIT 100',
                        'expected': 'Active user records'
                    }
                ]
            },
            {
                'pattern': 'SEARCH',
                'description': 'Queries searching for specific records',
                'triggers': ['find', 'search', 'get', 'lookup'],
                'examples': [
                    {
                        'query': 'Find student named John',
                        'sql': "SELECT * FROM students WHERE deleted = false AND name ILIKE '%John%' LIMIT 50",
                        'expected': 'Students with John in their name'
                    }
                ]
            },
            {
                'pattern': 'AGGREGATE',
                'description': 'Queries calculating statistics',
                'triggers': ['average', 'sum', 'max', 'min', 'statistics'],
                'examples': [
                    {
                        'query': 'Average attendance rate',
                        'sql': 'SELECT AVG(attendance_rate) as avg_rate FROM attendance_summary WHERE deleted = false',
                        'expected': 'Single average value'
                    }
                ]
            }
        ]
        
        documents = []
        
        for pattern_info in patterns:
            content = f"""
QUERY PATTERN: {pattern_info['pattern']}
{'=' * 80}

DESCRIPTION:
{pattern_info['description']}

TRIGGER WORDS:
{', '.join(pattern_info['triggers'])}

EXAMPLES WITH SQL:

"""
            for i, example in enumerate(pattern_info['examples'], 1):
                content += f"""
Example {i}:
User Query: "{example['query']}"
SQL Query: {example['sql']}
Expected Result: {example['expected']}

"""
            
            content += f"""
PATTERN RECOGNITION:
When user query contains words like: {', '.join(pattern_info['triggers'])}
→ Generate SQL following the {pattern_info['pattern']} pattern
→ Always include WHERE deleted = false for active records
→ Add LIMIT clause for safety (typically 100)
"""
            
            documents.append({
                'content': content.strip(),
                'metadata': {
                    'type': 'query_pattern',
                    'pattern': pattern_info['pattern'],
                    'priority': 'high',
                    'keywords': pattern_info['triggers']
                }
            })
        
        return documents
    
    def _create_business_logic_documents(self) -> List[Dict]:
        """Document business rules and logic"""
        
        documents = []
        
        # Soft delete logic
        documents.append({
            'content': """
BUSINESS LOGIC: SOFT DELETE PATTERN
{'=' * 80}

RULE: Records are never permanently deleted, only marked as deleted

IMPLEMENTATION:
- Tables have a 'deleted' boolean column
- deleted = false → Active record
- deleted = true → Deleted/Archived record

QUERY IMPLICATIONS:
✓ ALWAYS include: WHERE deleted = false
✓ Or use: WHERE (deleted = false OR deleted IS NULL)

EXAMPLES:
❌ WRONG: SELECT * FROM students
✓ RIGHT: SELECT * FROM students WHERE deleted = false

❌ WRONG: SELECT COUNT(*) FROM teachers
✓ RIGHT: SELECT COUNT(*) FROM teachers WHERE deleted = false

This ensures you only work with active, current data.
""",
            'metadata': {
                'type': 'business_logic',
                'topic': 'soft_delete',
                'priority': 'critical'
            }
        })
        
        # Role-based access
        documents.append({
            'content': """
BUSINESS LOGIC: ROLE-BASED ACCESS CONTROL
{'=' * 80}

ROLES IN SYSTEM:
1. Super Admin - Full system access
2. Teacher - Manage classes, students, grades
3. Student - View own records
4. Parent - View child's records

PERMISSION STRUCTURE:
- Roles have multiple permissions
- Permissions are specific actions (Read Student, Create User, etc.)
- Check user's role to determine capabilities

QUERYING PERMISSIONS:
To find what a role can do:
1. Query the roles table for role details
2. Join with role_permissions to get permission IDs
3. Join with permissions table to get permission details

Example: "What can a Teacher do?"
→ Look up Teacher role
→ Get associated permissions
→ List permission names and descriptions
""",
            'metadata': {
                'type': 'business_logic',
                'topic': 'permissions',
                'priority': 'high'
            }
        })
        
        return documents
    
    def _create_column_semantic_documents(self) -> List[Dict]:
        """Document what columns mean and contain"""
        
        documents = []
        
        # Common column patterns
        column_semantics = {
            'id': 'Primary key, unique identifier for each record',
            'uuid': 'Universal unique identifier, alternative to numeric ID',
            'name': 'Human-readable name or title',
            'email': 'Email address for contact (format: user@domain.com)',
            'phone': 'Phone number for contact',
            'created_at': 'Timestamp when record was created',
            'updated_at': 'Timestamp of last modification',
            'deleted': 'Boolean flag: false = active, true = deleted',
            'is_active': 'Boolean flag: true = active user, false = inactive',
            'user_id': 'Foreign key reference to users_user table',
            'student_id': 'Foreign key reference to students table',
            'teacher_id': 'Foreign key reference to teachers table',
            'class_id': 'Foreign key reference to classes table',
            'admission_number': 'Unique student enrollment identifier',
            'registration_number': 'Unique registration identifier',
            'date': 'Date field (format: YYYY-MM-DD)',
            'status': 'Current state (e.g., active, pending, completed)',
            'amount': 'Monetary value',
            'quantity': 'Numeric count',
            'description': 'Detailed text explanation',
            'notes': 'Additional comments or remarks'
        }
        
        content = """
COLUMN SEMANTICS GUIDE
{'=' * 80}

Understanding what columns mean helps generate better queries.

"""
        for col_name, meaning in column_semantics.items():
            content += f"\n{col_name}:\n  → {meaning}\n"
        
        content += """

USAGE IN QUERIES:

When user asks about:
- "emails" → Look for 'email' column
- "phone numbers" → Look for 'phone' or 'mobile' column
- "names" → Look for 'name', 'first_name', 'last_name' columns
- "when created" → Use 'created_at' column
- "active/inactive" → Check 'is_active' or 'deleted' columns

JOINING TABLES:
Foreign keys ending in '_id' reference other tables:
- user_id → JOIN with users_user table
- student_id → JOIN with students table
- teacher_id → JOIN with teachers table
"""
        
        documents.append({
            'content': content.strip(),
            'metadata': {
                'type': 'column_semantics',
                'priority': 'medium'
            }
        })
        
        return documents
    
    def _create_relationship_documents(self) -> List[Dict]:
        """Document table relationships"""
        
        documents = []
        
        relationships = [
            {
                'name': 'Student-Class Enrollment',
                'description': 'Students are enrolled in classes',
                'tables': ['students', 'classes', 'class_students'],
                'sql_example': """
-- Get students in a specific class
SELECT s.*, c.name as class_name
FROM students s
JOIN class_students cs ON s.id = cs.student_id
JOIN classes c ON cs.class_id = c.id
WHERE s.deleted = false 
AND c.deleted = false
"""
            },
            {
                'name': 'Teacher-Subject Assignment',
                'description': 'Teachers teach specific subjects',
                'tables': ['teachers', 'subjects', 'class_subjects'],
                'sql_example': """
-- Get subjects taught by a teacher
SELECT t.name as teacher_name, s.name as subject_name
FROM teachers t
JOIN class_subjects cs ON t.id = cs.teacher_id
JOIN subjects s ON cs.subject_id = s.id
WHERE t.deleted = false
AND s.deleted = false
"""
            }
        ]
        
        for rel in relationships:
            content = f"""
RELATIONSHIP: {rel['name']}
{'=' * 80}

{rel['description']}

TABLES INVOLVED:
{', '.join(rel['tables'])}

SQL EXAMPLE:
{rel['sql_example']}

QUERY PATTERNS:
- Use JOIN to connect related tables
- Always filter deleted = false on all tables
- Use meaningful aliases (s for students, t for teachers)
"""
            documents.append({
                'content': content.strip(),
                'metadata': {
                    'type': 'relationship',
                    'tables': rel['tables'],
                    'priority': 'medium'
                }
            })
        
        return documents
    
    # Helper methods
    
    def _get_best_table(self, table_names: List[str]) -> str:
        """Find which table actually exists"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = ANY(%s)
            """, [table_names])
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    def _get_detailed_schema(self, table_name: str) -> Dict:
        """Get detailed schema information"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, [table_name])
            
            columns = []
            primary_key = None
            
            for row in cursor.fetchall():
                col_info = {
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4]
                }
                columns.append(col_info)
                
                if row[0] == 'id':
                    primary_key = row[0]
            
            return {
                'columns': columns,
                'primary_key': primary_key or 'id'
            }
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample rows"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {table_name}
                    WHERE deleted = false
                    LIMIT %s
                """, [limit])
                
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
        except:
            return []
    
    def _get_row_count(self, table_name: str) -> int:
        """Get total row count"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM {table_name}
                    WHERE deleted = false
                """)
                return cursor.fetchone()[0]
        except:
            return 0
    
    def _format_schema(self, schema: Dict) -> str:
        """Format schema for display"""
        lines = []
        for col in schema['columns'][:10]:  # First 10 columns
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            line = f"  • {col['name']}: {col['type']} {nullable}"
            lines.append(line)
        
        if len(schema['columns']) > 10:
            lines.append(f"  ... and {len(schema['columns']) - 10} more columns")
        
        return "\n".join(lines)
    
    def _format_queries(self, queries: List[str]) -> str:
        """Format query list"""
        return "\n".join([f"  • {q}" for q in queries])
    
    def _format_relationships(self, relationships: Dict) -> str:
        """Format relationships"""
        return "\n".join([f"  • {entity}: {description}" 
                         for entity, description in relationships.items()])
    
    def _format_sample_data(self, sample_data: List[Dict]) -> str:
        """Format sample data"""
        if not sample_data:
            return "No sample data available"
        
        # Show column names and first few values
        first_row = sample_data[0]
        lines = [f"Columns: {', '.join(first_row.keys())}"]
        
        for i, row in enumerate(sample_data, 1):
            # Show first 5 fields of each sample row
            values = list(row.values())[:5]
            lines.append(f"Sample {i}: {', '.join(str(v)[:30] for v in values)}")
        
        return "\n".join(lines)
    
    def _extract_keywords(self, entity_name: str, entity_info: Dict) -> List[str]:
        """Extract keywords for better search"""
        keywords = [entity_name]
        
        # Add plural form
        if not entity_name.endswith('s'):
            keywords.append(entity_name + 's')
        
        # Add relationship keywords
        for rel in entity_info.get('relationships', {}).keys():
            keywords.append(rel)
        
        # Add common query words
        keywords.extend(['count', 'list', 'show', 'find', 'get'])
        
        return keywords


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    ingestion = ImprovedDataIngestion()
    documents = ingestion.generate_rich_knowledge_base()
    
    print(f"Generated {len(documents)} knowledge documents")
    
    # Show sample
    for doc in documents[:2]:
        print("\n" + "="*80)
        print(doc['content'][:500])
        print("\nMetadata:", doc['metadata'])