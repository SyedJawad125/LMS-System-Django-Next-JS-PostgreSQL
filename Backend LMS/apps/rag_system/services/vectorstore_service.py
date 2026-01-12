# ============================================
# ENHANCED VECTOR STORE SERVICE
# File: apps/rag_system/services/vectorstore_service.py
# ============================================

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional
from .database_connector import DatabaseConnector
import os
import json


class VectorStoreService:
    """Enhanced Vector Store with PostgreSQL integration"""
    
    def __init__(self, persist_directory: str = "./data/vectorstore"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        print("🚀 Initializing Enhanced Vector Store...")
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize ChromaDB
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="lms_knowledge"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        
        # Initialize database connector
        self.db_connector = DatabaseConnector()
        
        print("✅ Enhanced Vector Store initialized!")
    
    def initialize_with_database_knowledge(self, refresh: bool = False):
        """Initialize vector store with PostgreSQL database knowledge"""
        print("📚 Loading PostgreSQL database knowledge...")
        
        # Get all tables from database
        all_tables = self.db_connector.get_all_tables()
        print(f"📊 Found {len(all_tables)} tables in PostgreSQL")
        
        # Check if already initialized
        if not refresh:
            existing_count = self.vectorstore._collection.count()
            if existing_count > 100:
                print(f"✅ Vector store already initialized with {existing_count} documents")
                return
        
        # Create comprehensive documentation
        documentation = self._create_comprehensive_docs(all_tables)
        
        texts = [doc["content"] for doc in documentation]
        metadatas = [doc["metadata"] for doc in documentation]
        
        self.add_documents(texts, metadatas)
        print(f"✅ Initialized with {len(documentation)} knowledge documents")
    
    def _create_comprehensive_docs(self, tables: List[str]) -> List[Dict]:
        """Create comprehensive knowledge documents for all tables"""
        docs = []
        
        # Filter system tables
        user_tables = [t for t in tables if not any(
            skip in t.lower() for skip in ['django_', 'auth_permission', 'token_blacklist', 'celery']
        )]
        
        print(f"📋 Creating documentation for {len(user_tables)} user tables...")
        
        # Group tables by entity type
        table_groups = self._group_tables_by_entity(user_tables)
        
        # Create docs for each entity group
        for entity_type, entity_tables in table_groups.items():
            if entity_tables:
                try:
                    doc = self._create_entity_doc(entity_type, entity_tables)
                    docs.append(doc)
                except Exception as e:
                    print(f"⚠️ Error creating doc for {entity_type}: {e}")
        
        # Add query patterns
        docs.extend(self._create_query_pattern_docs())
        
        # Add general knowledge
        docs.extend(self._create_general_knowledge_docs())
        
        # Add table-specific documentation
        docs.extend(self._create_table_specific_docs(user_tables[:20]))  # Top 20 tables
        
        return docs
    
    def _group_tables_by_entity(self, tables: List[str]) -> Dict[str, List[str]]:
        """Group tables by entity type"""
        groups = {
            "user": [], "student": [], "teacher": [], "parent": [],
            "role": [], "class": [], "subject": [], "exam": [],
            "fee": [], "attendance": [], "vehicle": [], "route": [],
            "employee": [], "assignment": [], "leave": [], "message": [],
            "department": [], "course": [], "quiz": [], "certificate": [],
            "timetable": [], "book": [], "other": []
        }
        
        for table in tables:
            table_lower = table.lower()
            categorized = False
            
            # Check each entity type
            for entity in groups.keys():
                if entity == "other":
                    continue
                if entity in table_lower:
                    groups[entity].append(table)
                    categorized = True
                    break
            
            if not categorized:
                groups["other"].append(table)
        
        return groups
    
    def _create_entity_doc(self, entity_type: str, tables: List[str]) -> Dict:
        """Create documentation for an entity type"""
        main_table = tables[0]
        
        # Get actual schema from database
        schema_info = self.db_connector.get_table_schema_info(main_table)
        columns = schema_info.get("columns", [])
        row_count = schema_info.get("row_count", 0)
        
        content = f"""
{entity_type.upper()} ENTITY INFORMATION
{'=' * 50}

PRIMARY TABLE: {main_table}
ALL RELATED TABLES: {', '.join(tables)}
TOTAL RECORDS: {row_count}

AVAILABLE COLUMNS:
{', '.join(columns[:15])}
{f'... and {len(columns)-15} more columns' if len(columns) > 15 else ''}

COMMON QUERIES:

1. COUNT QUERIES:
   - "How many {entity_type}s are there?"
   - "Count total {entity_type}s"
   - "Number of active {entity_type}s"

2. LIST QUERIES:
   - "Show all {entity_type}s"
   - "List {entity_type} names"
   - "Display {entity_type} information"

3. FILTER QUERIES:
   - "Find {entity_type} by name"
   - "Search {entity_type}s with email"
   - "{entity_type}s created this month"

4. DETAIL QUERIES:
   - "Get {entity_type} details"
   - "{entity_type} information for [name]"
   - "Show {entity_type} profile"

RESPONSE EXAMPLES:

Q: "How many {entity_type}s?"
A: "There are approximately {row_count} {entity_type}s in the system."

Q: "Show {entity_type}s"
A: "I can retrieve {entity_type} information from the {main_table} table."

Q: "Find {entity_type} details"
A: "I can search for {entity_type}s by: {', '.join(columns[:5])}"

TABLE STRUCTURE:
The {main_table} table contains {len(columns)} columns including:
{self._format_column_list(columns[:10])}

IMPORTANT NOTES:
- Use table name: {main_table}
- Total records: {row_count}
- Check 'deleted' field for active records
- Join with related tables if needed: {', '.join(tables[1:3]) if len(tables) > 1 else 'None'}
"""
        
        return {
            "content": content.strip(),
            "metadata": {
                "type": "entity_knowledge",
                "entity": entity_type,
                "main_table": main_table,
                "tables_count": len(tables),
                "row_count": row_count,
                "priority": "high"
            }
        }
    
    def _format_column_list(self, columns: List[str]) -> str:
        """Format columns for display"""
        return "\n".join([f"  • {col}" for col in columns])
    
    def _create_table_specific_docs(self, tables: List[str]) -> List[Dict]:
        """Create specific documentation for important tables"""
        docs = []
        
        for table in tables:
            try:
                schema_info = self.db_connector.get_table_schema_info(table)
                
                content = f"""
TABLE: {table}
{'=' * 50}

COLUMNS: {', '.join(schema_info.get('columns', [])[:10])}
RECORDS: {schema_info.get('row_count', 0)}
ENTITY TYPE: {schema_info.get('entity_type', 'unknown')}

USAGE:
- Direct table reference: {table}
- Use for queries about {schema_info.get('entity_type', 'data')}
- Check 'deleted' field for active records

SQL EXAMPLES:
- Count: SELECT COUNT(*) FROM {table} WHERE (deleted = FALSE OR deleted IS NULL)
- List: SELECT * FROM {table} WHERE (deleted = FALSE OR deleted IS NULL) LIMIT 100
"""
                
                docs.append({
                    "content": content.strip(),
                    "metadata": {
                        "type": "table_specific",
                        "table_name": table,
                        "entity": schema_info.get('entity_type', 'unknown'),
                        "priority": "medium"
                    }
                })
            except Exception as e:
                print(f"⚠️ Error creating doc for {table}: {e}")
        
        return docs
    
    def _create_query_pattern_docs(self) -> List[Dict]:
        """Create query pattern documentation"""
        patterns = [
            {
                "content": """
COUNTING QUERIES
{'=' * 50}

PATTERNS:
• "How many X"
• "Count X"
• "Total number of X"
• "Number of X"

EXAMPLES:
• "How many users?" → Count from users_user table
• "Total students?" → Count from students table
• "Number of teachers?" → Count from teachers table

SQL PATTERN:
SELECT COUNT(*) FROM [table] WHERE (deleted = FALSE OR deleted IS NULL)

RESPONSE FORMAT:
"There are [number] [entity]s in the system."
""",
                "metadata": {"type": "query_pattern", "pattern": "counting"}
            },
            {
                "content": """
LISTING QUERIES
{'=' * 50}

PATTERNS:
• "Show X"
• "List X"
• "Display X"
• "Get all X"

EXAMPLES:
• "Show all users" → List from users_user
• "List students" → List from students
• "Display teachers" → List from teachers

SQL PATTERN:
SELECT * FROM [table] WHERE (deleted = FALSE OR deleted IS NULL) LIMIT 100

RESPONSE FORMAT:
"Here are the [entity]s: [list]"
""",
                "metadata": {"type": "query_pattern", "pattern": "listing"}
            },
            {
                "content": """
FILTERING QUERIES
{'=' * 50}

PATTERNS:
• "X with [column]"
• "X where [condition]"
• "Find X by [field]"

EXAMPLES:
• "Users with email gmail.com"
• "Students in class 10"
• "Teachers with experience > 5"

SQL PATTERN:
SELECT * FROM [table] WHERE [condition] AND (deleted = FALSE OR deleted IS NULL)

RESPONSE FORMAT:
"Found [number] [entity]s matching [criteria]"
""",
                "metadata": {"type": "query_pattern", "pattern": "filtering"}
            }
        ]
        
        return patterns
    
    def _create_general_knowledge_docs(self) -> List[Dict]:
        """Create general system knowledge"""
        docs = [
            {
                "content": """
LMS SYSTEM DATABASE OVERVIEW
{'=' * 50}

This is a Learning Management System (LMS) with comprehensive PostgreSQL database.

MAIN ENTITIES:
• Users (users_user, auth_user)
• Students (students)
• Teachers (teachers)
• Parents (parents)
• Classes (classes)
• Subjects (subjects)
• Exams (exams, exam_results, exam_schedules)
• Fees (fee_invoices, fee_payments, fee_structures)
• Attendance (daily_attendance, attendance_summary)
• Vehicles & Routes (vehicles, routes, transport_allocations)
• Assignments (assignments, assignment_submissions)
• Leaves (leave_applications, leave_balances)
• Departments (departments)
• Certificates (certificates, certificate_templates)

TABLE NAMING CONVENTIONS:
- Some tables have prefixes (users_user, users_role)
- Some are plural without prefix (students, teachers)
- Some have underscore separation (fee_invoices, exam_results)

IMPORTANT FIELDS:
- Most tables have 'deleted' field for soft deletes
- Check (deleted = FALSE OR deleted IS NULL) for active records
- Common fields: id, created_at, updated_at, deleted

QUERY GUIDELINES:
1. Always specify exact table name
2. Filter deleted records
3. Use appropriate JOINs for related data
4. Limit results for performance
""",
                "metadata": {"type": "system_overview", "priority": "high"}
            }
        ]
        
        return docs
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """Add documents to vector store"""
        if not texts:
            return
        
        chunks = []
        chunk_metadatas = []
        
        for i, text in enumerate(texts):
            if not text or len(text.strip()) == 0:
                continue
            
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            
            # Split into chunks
            text_chunks = self.text_splitter.split_text(text)
            chunks.extend(text_chunks)
            chunk_metadatas.extend([metadata] * len(text_chunks))
        
        if chunks:
            self.vectorstore.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas
            )
            print(f"📚 Added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, k: int = 10) -> List[Dict]:
        """Search for relevant information with query expansion"""
        try:
            # Expand query
            expanded_queries = self._expand_query(query)
            
            all_results = []
            seen_contents = set()
            
            for expanded_query in expanded_queries[:3]:  # Top 3 expansions
                results = self.vectorstore.similarity_search_with_score(
                    expanded_query, 
                    k=k
                )
                
                for doc, score in results:
                    content_hash = hash(doc.page_content[:100])
                    if content_hash not in seen_contents:
                        seen_contents.add(content_hash)
                        all_results.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "score": float(1 - score),  # Convert to similarity
                            "query": expanded_query
                        })
            
            # Sort by score and return top k
            all_results.sort(key=lambda x: x["score"], reverse=True)
            return all_results[:k]
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with variations"""
        query_lower = query.lower()
        expansions = [query]
        
        # Entity synonyms
        synonyms = {
            "user": ["account", "profile"],
            "student": ["pupil", "learner"],
            "teacher": ["instructor", "faculty"],
            "class": ["grade", "section"],
            "exam": ["test", "assessment"],
            "fee": ["payment", "invoice"]
        }
        
        for entity, syns in synonyms.items():
            if entity in query_lower:
                for syn in syns:
                    expansions.append(query_lower.replace(entity, syn))
        
        # Query type variations
        if "how many" in query_lower:
            expansions.append(query_lower.replace("how many", "count"))
        if "show" in query_lower:
            expansions.append(query_lower.replace("show", "list"))
        
        return list(set(expansions))
    
    def stats(self) -> Dict:
        """Get vector store statistics"""
        try:
            count = self.vectorstore._collection.count()
            return {
                "total_documents": count,
                "status": "operational" if count > 0 else "empty",
                "persist_directory": self.persist_directory
            }
        except:
            return {
                "total_documents": 0,
                "status": "error",
                "persist_directory": self.persist_directory
            }