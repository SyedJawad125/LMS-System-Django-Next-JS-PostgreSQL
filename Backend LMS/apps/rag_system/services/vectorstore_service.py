# # VECTOR STORE CODE
# from langchain_chroma import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from typing import List, Dict, Optional
# import os
# import json


# class VectorStoreService:
#     """Enhanced Vector Store that handles ALL queries"""
    
#     def __init__(self, persist_directory: str = "./data/vectorstore"):
#         self.persist_directory = persist_directory
#         os.makedirs(persist_directory, exist_ok=True)
        
#         # Initialize embeddings
#         print("🚀 Initializing Vector Store...")
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2",
#             model_kwargs={'device': 'cpu'}
#         )
        
#         # Initialize ChromaDB
#         self.vectorstore = Chroma(
#             persist_directory=persist_directory,
#             embedding_function=self.embeddings,
#             collection_name="lms_knowledge"
#         )
        
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=800,
#             chunk_overlap=150,
#         )
        
#         print("✅ Vector Store initialized successfully!")
    
#     def initialize_with_database_knowledge(self, all_tables: List[str]):
#         """Initialize vector store with comprehensive database knowledge"""
#         print(f"📚 Loading database knowledge for {len(all_tables)} tables...")
        
#         # Add comprehensive documentation
#         documentation = self._create_comprehensive_docs(all_tables)
        
#         texts = [doc["content"] for doc in documentation]
#         metadatas = [doc["metadata"] for doc in documentation]
        
#         self.add_documents(texts, metadatas)
#         print(f"✅ Added {len(documentation)} knowledge documents")
    
#     def _create_comprehensive_docs(self, tables: List[str]) -> List[Dict]:
#         """Create comprehensive knowledge documents for all tables"""
#         docs = []
        
#         # Group tables by entity type
#         table_groups = self._group_tables_by_entity(tables)
        
#         # Create docs for each entity group
#         for entity_type, entity_tables in table_groups.items():
#             if entity_tables:
#                 doc = self._create_entity_doc(entity_type, entity_tables)
#                 docs.append(doc)
        
#         # Add query patterns
#         docs.extend(self._create_query_pattern_docs())
        
#         # Add general knowledge
#         docs.extend(self._create_general_knowledge_docs())
        
#         return docs
    
#     def _group_tables_by_entity(self, tables: List[str]) -> Dict[str, List[str]]:
#         """Group tables by entity type"""
#         groups = {
#             "user": [],
#             "student": [],
#             "teacher": [],
#             "role": [],
#             "class": [],
#             "subject": [],
#             "exam": [],
#             "fee": [],
#             "attendance": [],
#             "vehicle": [],
#             "route": [],
#             "parent": [],
#             "book": [],
#             "employee": [],
#             "other": []
#         }
        
#         entity_keywords = {
#             "user": ["user", "account"],
#             "student": ["student", "pupil"],
#             "teacher": ["teacher", "faculty", "instructor"],
#             "role": ["role", "permission"],
#             "class": ["class", "grade", "section"],
#             "subject": ["subject", "course"],
#             "exam": ["exam", "test", "result"],
#             "fee": ["fee", "payment", "invoice"],
#             "attendance": ["attendance"],
#             "vehicle": ["vehicle", "bus", "transport"],
#             "route": ["route"],
#             "parent": ["parent", "guardian"],
#             "book": ["book", "library", "image"],
#             "employee": ["employee", "staff"]
#         }
        
#         for table in tables:
#             table_lower = table.lower()
#             categorized = False
            
#             for entity, keywords in entity_keywords.items():
#                 for keyword in keywords:
#                     if keyword in table_lower:
#                         groups[entity].append(table)
#                         categorized = True
#                         break
#                 if categorized:
#                     break
            
#             if not categorized:
#                 groups["other"].append(table)
        
#         return groups
    
#     def _create_entity_doc(self, entity_type: str, tables: List[str]) -> Dict:
#         """Create documentation for an entity type"""
#         # Find the main table
#         main_table = self._find_main_table(tables)
        
#         # Common columns for this entity
#         common_columns = self._get_common_columns(entity_type)
        
#         # Example queries
#         example_queries = self._get_example_queries(entity_type, main_table)
        
#         content = f"""
#         {entity_type.upper()} INFORMATION
#         ======================
        
#         MAIN TABLE: {main_table}
#         ALL TABLES: {', '.join(tables)}
        
#         DESCRIPTION:
#         This entity stores {entity_type}-related information in the LMS system.
        
#         COMMON COLUMNS:
#         {', '.join(common_columns)}
        
#         EXAMPLE DATA QUERIES:
        
#         1. Count {entity_type}s:
#            "How many {entity_type}s are there?"
#            "Count {entity_type}s"
#            "Total number of {entity_type}s"
           
#         2. List {entity_type}s:
#            "Show all {entity_type}s"
#            "List {entity_type}s"
#            "Display {entity_type} information"
           
#         3. Find specific {entity_type}s:
#            "Find {entity_type} with name X"
#            "Search for {entity_type} by email"
#            "Get {entity_type} details"
           
#         4. Filter {entity_type}s:
#            "Active {entity_type}s"
#            "{entity_type}s created this month"
#            "{entity_type}s with status X"
        
#         SAMPLE ANSWERS:
        
#         Q: "How many {entity_type}s are there?"
#         A: "There are [count] {entity_type}s in the system."
        
#         Q: "Show all {entity_type}s"
#         A: "Here are the {entity_type}s: [list of names/emails]"
        
#         Q: "Find {entity_type} John"
#         A: "John's details: [details]"
        
#         IMPORTANT NOTES:
#         - Always check multiple tables if information isn't found
#         - Use appropriate table names (some have prefixes)
#         - Consider soft-deleted records
#         """
        
#         return {
#             "content": content.strip(),
#             "metadata": {
#                 "type": "entity_knowledge",
#                 "entity": entity_type,
#                 "main_table": main_table,
#                 "tables_count": len(tables),
#                 "priority": "high"
#             }
#         }
    
#     def _find_main_table(self, tables: List[str]) -> str:
#         """Find the main table from a list"""
#         if not tables:
#             return "unknown"
        
#         # Prefer simple table names
#         simple_tables = [t for t in tables if '_' not in t]
#         if simple_tables:
#             return simple_tables[0]
        
#         # Otherwise return first table
#         return tables[0]
    
#     def _get_common_columns(self, entity_type: str) -> List[str]:
#         """Get common columns for an entity type"""
#         column_map = {
#             "user": ["id", "username", "email", "first_name", "last_name", "is_active", "created_at"],
#             "student": ["id", "name", "roll_number", "class_id", "parent_id", "admission_date"],
#             "teacher": ["id", "name", "qualification", "experience", "department", "designation"],
#             "role": ["id", "name", "description", "permissions", "created_at"],
#             "class": ["id", "name", "grade", "section", "class_teacher_id", "capacity"],
#             "subject": ["id", "name", "code", "description", "credits"],
#             "exam": ["id", "name", "type", "total_marks", "date", "subject_id"],
#             "fee": ["id", "student_id", "amount", "due_date", "paid_amount", "status"],
#             "attendance": ["id", "student_id", "date", "status", "remarks"],
#             "vehicle": ["id", "number", "driver_name", "capacity", "route_id"],
#             "route": ["id", "name", "start_point", "end_point", "distance"],
#             "parent": ["id", "name", "email", "phone", "occupation"],
#             "book": ["id", "title", "author", "isbn", "publisher", "available_copies"],
#             "employee": ["id", "name", "designation", "department", "salary", "joining_date"]
#         }
        
#         return column_map.get(entity_type, ["id", "name", "created_at"])
    
#     def _get_example_queries(self, entity_type: str, main_table: str) -> List[str]:
#         """Get example queries for an entity"""
#         examples = [
#             f"How many {entity_type}s?",
#             f"Count {entity_type}s",
#             f"List all {entity_type}s",
#             f"Show {entity_type} details",
#             f"Find {entity_type} by name",
#             f"Active {entity_type}s",
#             f"Latest {entity_type}s",
#             f"{entity_type} statistics"
#         ]
        
#         if entity_type in ["student", "teacher", "employee"]:
#             examples.extend([
#                 f"{entity_type} contact information",
#                 f"{entity_type} enrollment/joining date",
#                 f"{entity_type} performance"
#             ])
        
#         return examples
    
#     def _create_query_pattern_docs(self) -> List[Dict]:
#         """Create query pattern documentation"""
#         patterns = [
#             {
#                 "content": """
#                 QUERY TYPE: COUNTING QUERIES
#                 ============================
                
#                 PATTERNS:
#                 - "How many X"
#                 - "Count X"
#                 - "Total number of X"
#                 - "Number of X"
                
#                 EXAMPLES:
#                 - "How many users are there?"
#                 - "Count all students"
#                 - "Total number of teachers"
#                 - "Number of active classes"
                
#                 RESPONSE FORMAT:
#                 - "There are [number] [entity]s in the system."
#                 - "The total count is [number]."
#                 - "Currently, there are [number] [entity]s."
                
#                 TIPS:
#                 - Always provide the exact number if known
#                 - Mention if data is approximate
#                 - Specify time period if relevant
#                 """,
#                 "metadata": {
#                     "type": "query_pattern",
#                     "pattern": "counting",
#                     "category": "analytical"
#                 }
#             },
#             {
#                 "content": """
#                 QUERY TYPE: LISTING QUERIES
#                 ===========================
                
#                 PATTERNS:
#                 - "Show X"
#                 - "List X"
#                 - "Display X"
#                 - "Get all X"
#                 - "What are the X"
                
#                 EXAMPLES:
#                 - "Show all users"
#                 - "List students in grade 10"
#                 - "Display teacher names"
#                 - "Get all classes"
                
#                 RESPONSE FORMAT:
#                 - "Here are the [entity]s: [list]"
#                 - "The [entity]s include: [list]"
#                 - "Available [entity]s: [list]"
                
#                 TIPS:
#                 - Limit lists to 10 items maximum
#                 - Group similar items
#                 - Provide summaries for large lists
#                 """,
#                 "metadata": {
#                     "type": "query_pattern",
#                     "pattern": "listing",
#                     "category": "factual"
#                 }
#             },
#             {
#                 "content": """
#                 QUERY TYPE: DETAIL QUERIES
#                 ==========================
                
#                 PATTERNS:
#                 - "Details of X"
#                 - "Information about X"
#                 - "Tell me about X"
#                 - "What is X"
#                 - "Explain X"
                
#                 EXAMPLES:
#                 - "Details of student John"
#                 - "Information about the Math class"
#                 - "Tell me about the fee structure"
#                 - "What is the attendance policy"
                
#                 RESPONSE FORMAT:
#                 - "[Entity] details: [information]"
#                 - "Here's what I know about [entity]: [details]"
#                 - "The [entity] information: [details]"
                
#                 TIPS:
#                 - Provide comprehensive information
#                 - Include relevant context
#                 - Mention related entities
#                 """,
#                 "metadata": {
#                     "type": "query_pattern",
#                     "pattern": "details",
#                     "category": "informational"
#                 }
#             },
#             {
#                 "content": """
#                 QUERY TYPE: COLUMN-SPECIFIC QUERIES
#                 ====================================
                
#                 PATTERNS:
#                 - "X with [column] Y"
#                 - "Find X where [column]"
#                 - "X having [column]"
#                 - "X [column] information"
                
#                 EXAMPLES:
#                 - "Users with email gmail.com"
#                 - "Students in class 10"
#                 - "Teachers with experience > 5 years"
#                 - "Fee payments for January"
                
#                 RESPONSE FORMAT:
#                 - "Here are the [entity]s with [criteria]: [list/details]"
#                 - "Found [number] [entity]s matching [criteria]"
#                 - "The [entity]s meeting [criteria] are: [information]"
                
#                 TIPS:
#                 - Be specific about column values
#                 - Mention if no matches found
#                 - Suggest alternative criteria if needed
#                 """,
#                 "metadata": {
#                     "type": "query_pattern",
#                     "pattern": "column_filter",
#                     "category": "filtering"
#                 }
#             }
#         ]
        
#         return patterns
    
#     def _create_general_knowledge_docs(self) -> List[Dict]:
#         """Create general knowledge documentation"""
#         docs = [
#             {
#                 "content": """
#                 LMS SYSTEM OVERVIEW
#                 ===================
                
#                 This Learning Management System (LMS) manages:
                
#                 1. USER MANAGEMENT:
#                    - Students, Teachers, Parents, Employees
#                    - User roles and permissions
#                    - Authentication and profiles
                
#                 2. ACADEMIC MANAGEMENT:
#                    - Classes and sections
#                    - Subjects and courses
#                    - Exams and results
#                    - Attendance tracking
                
#                 3. FINANCIAL MANAGEMENT:
#                    - Fee structures and invoices
#                    - Payments and discounts
#                    - Financial reports
                
#                 4. OPERATIONAL MANAGEMENT:
#                    - Vehicle and transport
#                    - Routes and schedules
#                    - Library and books
#                    - Hostel facilities
                
#                 COMMON QUERIES ANSWERED:
#                 - User counts and lists
#                 - Academic information
#                 - Financial details
#                 - Operational data
                
#                 RESPONSE GUIDELINES:
#                 - Always provide accurate information
#                 - Be specific with numbers
#                 - Mention data sources
#                 - Be helpful and clear
#                 """,
#                 "metadata": {
#                     "type": "system_overview",
#                     "category": "general",
#                     "priority": "high"
#                 }
#             },
#             {
#                 "content": """
#                 HOW TO ASK QUESTIONS
#                 ====================
                
#                 FOR BEST RESULTS:
                
#                 1. Be specific:
#                    ✅ "How many students in grade 10?"
#                    ❌ "Tell me about students"
                
#                 2. Use clear entity names:
#                    ✅ "List all teachers"
#                    ✅ "Count vehicles"
#                    ✅ "Show fee payments"
                
#                 3. Specify columns when needed:
#                    ✅ "Students with attendance > 90%"
#                    ✅ "Teachers in Science department"
#                    ✅ "Fee invoices for January 2024"
                
#                 4. Ask follow-up questions:
#                    ✅ "Now show me their details"
#                    ✅ "What about inactive users?"
#                    ✅ "Compare with last month"
                
#                 EXAMPLE DIALOGUES:
                
#                 User: "How many active users?"
#                 Assistant: "There are 245 active users in the system."
                
#                 User: "Show me science teachers"
#                 Assistant: "Science teachers: John (Physics), Sarah (Chemistry), Mike (Biology)"
                
#                 User: "Students in class 10A"
#                 Assistant: "Class 10A students: Alice, Bob, Charlie, Diana (total: 4)"
#                 """,
#                 "metadata": {
#                     "type": "query_guidance",
#                     "category": "help",
#                     "priority": "medium"
#                 }
#             }
#         ]
        
#         return docs
    
#     def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
#         """Add documents to vector store"""
#         if not texts:
#             return
        
#         chunks = []
#         chunk_metadatas = []
        
#         for i, text in enumerate(texts):
#             if not text or len(text.strip()) == 0:
#                 continue
            
#             metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            
#             # Split into chunks
#             text_chunks = self.text_splitter.split_text(text)
#             chunks.extend(text_chunks)
#             chunk_metadatas.extend([metadata] * len(text_chunks))
        
#         if chunks:
#             self.vectorstore.add_texts(
#                 texts=chunks,
#                 metadatas=chunk_metadatas
#             )
#             print(f"📚 Added {len(chunks)} chunks to vector store")
    
#     def search(self, query: str, k: int = 10) -> List[Dict]:
#         """Search for relevant information"""
#         try:
#             # Enhanced search with query expansion
#             expanded_queries = self._expand_query(query)
            
#             all_results = []
            
#             for expanded_query in expanded_queries:
#                 results = self.vectorstore.similarity_search_with_score(
#                     expanded_query, 
#                     k=k
#                 )
                
#                 for doc, score in results:
#                     all_results.append({
#                         "content": doc.page_content,
#                         "metadata": doc.metadata,
#                         "score": float(score),
#                         "query": expanded_query
#                     })
            
#             # Remove duplicates and sort by score
#             unique_results = []
#             seen_contents = set()
            
#             for result in sorted(all_results, key=lambda x: x["score"], reverse=True):
#                 content_hash = hash(result["content"][:200])
#                 if content_hash not in seen_contents:
#                     seen_contents.add(content_hash)
#                     unique_results.append(result)
            
#             return unique_results[:k]
            
#         except Exception as e:
#             print(f"❌ Search error: {e}")
#             return []
    
#     def _expand_query(self, query: str) -> List[str]:
#         """Expand query with variations"""
#         query_lower = query.lower()
#         expansions = [query]
        
#         # Add entity variations
#         entity_variations = {
#             "user": ["account", "profile", "member"],
#             "student": ["pupil", "learner"],
#             "teacher": ["instructor", "faculty", "staff"],
#             "class": ["grade", "section", "form"],
#             "exam": ["test", "assessment"],
#             "fee": ["payment", "invoice", "bill"],
#             "vehicle": ["bus", "transport"],
#             "book": ["publication", "title", "library"]
#         }
        
#         for entity, variations in entity_variations.items():
#             if entity in query_lower:
#                 for variation in variations:
#                     expanded = query_lower.replace(entity, variation)
#                     expansions.append(expanded)
        
#         # Add question variations
#         if "how many" in query_lower:
#             expansions.append(query_lower.replace("how many", "count"))
#             expansions.append(query_lower.replace("how many", "total number of"))
        
#         if "show" in query_lower:
#             expansions.append(query_lower.replace("show", "list"))
#             expansions.append(query_lower.replace("show", "display"))
        
#         return list(set(expansions))
    
#     def generate_answer(self, query: str, search_results: List[Dict]) -> str:
#         """Generate answer from search results"""
#         if not search_results:
#             return "I don't have specific information about that in my knowledge base."
        
#         # Extract relevant information
#         entity_info = self._extract_entity_info(query, search_results)
#         patterns = self._extract_patterns(query, search_results)
        
#         # Build answer
#         answer_parts = []
        
#         if entity_info:
#             answer_parts.append(entity_info)
        
#         if patterns:
#             answer_parts.append(patterns)
        
#         # Add general guidance if needed
#         if not answer_parts:
#             answer_parts.append(self._provide_general_guidance(query))
        
#         return "\n\n".join(answer_parts)
    
#     def _extract_entity_info(self, query: str, results: List[Dict]) -> str:
#         """Extract entity-specific information"""
#         query_lower = query.lower()
        
#         # Find entity type
#         entities = ["user", "student", "teacher", "role", "class", 
#                    "subject", "exam", "fee", "attendance", "vehicle", 
#                    "route", "parent", "book", "employee"]
        
#         entity_type = None
#         for entity in entities:
#             if entity in query_lower:
#                 entity_type = entity
#                 break
        
#         if not entity_type:
#             return ""
        
#         # Find entity knowledge
#         entity_knowledge = []
#         for result in results:
#             metadata = result.get("metadata", {})
#             if metadata.get("entity") == entity_type or metadata.get("type") == "entity_knowledge":
#                 content = result.get("content", "")
                
#                 # Extract example queries section
#                 if "EXAMPLE DATA QUERIES:" in content:
#                     start = content.find("EXAMPLE DATA QUERIES:")
#                     end = content.find("SAMPLE ANSWERS:", start)
#                     if end == -1:
#                         end = len(content)
                    
#                     example_section = content[start:end].strip()
#                     entity_knowledge.append(example_section)
                
#                 # Extract sample answers
#                 if "SAMPLE ANSWERS:" in content:
#                     start = content.find("SAMPLE ANSWERS:")
#                     sample_section = content[start:].strip()
#                     entity_knowledge.append(sample_section)
        
#         if entity_knowledge:
#             return f"**{entity_type.upper()} INFORMATION**\n\n" + "\n\n".join(entity_knowledge[:3])
        
#         return ""
    
#     def _extract_patterns(self, query: str, results: List[Dict]) -> str:
#         """Extract query patterns"""
#         patterns = []
        
#         for result in results:
#             metadata = result.get("metadata", {})
#             if metadata.get("type") == "query_pattern":
#                 content = result.get("content", "")
                
#                 # Check if pattern matches query
#                 query_lower = query.lower()
#                 pattern = metadata.get("pattern", "")
                
#                 if pattern == "counting" and any(word in query_lower for word in ["how many", "count", "total"]):
#                     patterns.append(content)
#                 elif pattern == "listing" and any(word in query_lower for word in ["show", "list", "display"]):
#                     patterns.append(content)
#                 elif pattern == "details" and any(word in query_lower for word in ["details", "information", "tell me about"]):
#                     patterns.append(content)
#                 elif pattern == "column_filter" and any(word in query_lower for word in ["with", "where", "having"]):
#                     patterns.append(content)
        
#         if patterns:
#             return "**QUERY GUIDANCE**\n\n" + "\n\n".join(patterns[:2])
        
#         return ""
    
#     def _provide_general_guidance(self, query: str) -> str:
#         """Provide general guidance for the query"""
#         query_lower = query.lower()
        
#         if any(word in query_lower for word in ["how", "what", "where", "when", "why"]):
#             return """
#             **GENERAL INFORMATION**
            
#             For detailed queries about the LMS system:
            
#             1. Be specific about what you want to know
#             2. Mention specific entities (users, students, teachers, etc.)
#             3. Specify time periods if relevant
#             4. Ask follow-up questions for more details
            
#             Example: Instead of "Tell me about users", try:
#             - "How many active users are there?"
#             - "List users created this month"
#             - "Show user roles and permissions"
#             """
        
#         return """
#         **HOW TO GET INFORMATION**
        
#         To get specific information from the LMS system, you can ask about:
        
#         • User counts and lists
#         • Student/Teacher information  
#         • Academic records
#         • Financial data
#         • Operational details
        
#         Try questions like:
#         - "How many [entity]s?"
#         - "Show all [entity]s"
#         - "[Entity] details for [specific criteria]"
#         """

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