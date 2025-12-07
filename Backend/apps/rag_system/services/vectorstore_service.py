# from langchain_chroma import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from typing import List, Dict
# import os


# class VectorStoreService:
#     """ChromaDB Vector Store Service"""
    
#     def __init__(self, persist_directory: str = "./data/vectorstore"):
#         self.persist_directory = persist_directory
#         os.makedirs(persist_directory, exist_ok=True)
        
#         # Initialize embeddings
#         print("Initializing embeddings model...")
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2",
#             model_kwargs={'device': 'cpu'}
#         )
        
#         # Initialize ChromaDB
#         print("Initializing ChromaDB...")
#         self.vectorstore = Chroma(
#             persist_directory=persist_directory,
#             embedding_function=self.embeddings,
#             collection_name="lms_knowledge"
#         )
        
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len,
#         )
#         print("VectorStore initialized successfully!")
    
#     def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
#         """Add documents to vector store"""
#         if not texts:
#             return
        
#         # Split texts into chunks
#         chunks = []
#         chunk_metadatas = []
        
#         for i, text in enumerate(texts):
#             if not text or len(text.strip()) == 0:
#                 continue
                
#             text_chunks = self.text_splitter.split_text(text)
#             chunks.extend(text_chunks)
            
#             # Replicate metadata for each chunk
#             metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
#             chunk_metadatas.extend([metadata] * len(text_chunks))
        
#         if chunks:
#             # Add to vector store
#             self.vectorstore.add_texts(
#                 texts=chunks,
#                 metadatas=chunk_metadatas
#             )
#             print(f"Added {len(chunks)} chunks to vector store")
    
#     def search(self, query: str, k: int = 5) -> List[Dict]:
#         """Search similar documents"""
#         try:
#             results = self.vectorstore.similarity_search_with_score(query, k=k)
            
#             return [
#                 {
#                     "content": doc.page_content,
#                     "metadata": doc.metadata,
#                     "score": float(score)
#                 }
#                 for doc, score in results
#             ]
#         except Exception as e:
#             print(f"Vector search error: {e}")
#             return []
    
#     def add_database_context(self, table_name: str, data: List[Dict]):
#         """Add database records to vector store"""
#         if not data:
#             return
        
#         texts = []
#         metadatas = []
        
#         for record in data:
#             # Convert record to text
#             text = f"Table: {table_name}\n"
#             text += "\n".join([f"{k}: {v}" for k, v in record.items() if v is not None])
#             texts.append(text)
            
#             metadatas.append({
#                 "source": "database",
#                 "table": table_name,
#                 "record_id": str(record.get('id', ''))
#             })
        
#         self.add_documents(texts, metadatas)
#         print(f"Indexed {len(texts)} records from {table_name}")







# # ============================================
# # FILE 9: apps/rag_system/services/vectorstore_service.py
# # ============================================

# from langchain_chroma import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from typing import List, Dict
# import os


# class VectorStoreService:
#     """ChromaDB Vector Store Service"""
    
#     def __init__(self, persist_directory: str = "./data/vectorstore"):
#         self.persist_directory = persist_directory
#         os.makedirs(persist_directory, exist_ok=True)
        
#         # Initialize embeddings
#         print("Initializing embeddings model...")
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2",
#             model_kwargs={'device': 'cpu'}
#         )
        
#         # Initialize ChromaDB
#         print("Initializing ChromaDB...")
#         self.vectorstore = Chroma(
#             persist_directory=persist_directory,
#             embedding_function=self.embeddings,
#             collection_name="lms_knowledge"
#         )
        
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len,
#         )
#         print("VectorStore initialized successfully!")
    
#     def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
#         """Add documents to vector store"""
#         if not texts:
#             return
        
#         # Split texts into chunks
#         chunks = []
#         chunk_metadatas = []
        
#         for i, text in enumerate(texts):
#             if not text or len(text.strip()) == 0:
#                 continue
                
#             text_chunks = self.text_splitter.split_text(text)
#             chunks.extend(text_chunks)
            
#             # Replicate metadata for each chunk
#             metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
#             chunk_metadatas.extend([metadata] * len(text_chunks))
        
#         if chunks:
#             # Add to vector store
#             self.vectorstore.add_texts(
#                 texts=chunks,
#                 metadatas=chunk_metadatas
#             )
#             print(f"Added {len(chunks)} chunks to vector store")
    
#     def search(self, query: str, k: int = 5) -> List[Dict]:
#         """Search similar documents"""
#         try:
#             results = self.vectorstore.similarity_search_with_score(query, k=k)
            
#             return [
#                 {
#                     "content": doc.page_content,
#                     "metadata": doc.metadata,
#                     "score": float(score)
#                 }
#                 for doc, score in results
#             ]
#         except Exception as e:
#             print(f"Vector search error: {e}")
#             return []
    
#     def add_database_context(self, table_name: str, data: List[Dict]):
#         """Add database records to vector store"""
#         if not data:
#             return
        
#         texts = []
#         metadatas = []
        
#         for record in data:
#             # Convert record to text
#             text = f"Table: {table_name}\n"
#             text += "\n".join([f"{k}: {v}" for k, v in record.items() if v is not None])
#             texts.append(text)
            
#             metadatas.append({
#                 "source": "database",
#                 "table": table_name,
#                 "record_id": str(record.get('id', ''))
#             })
        
#         self.add_documents(texts, metadatas)
#         print(f"Indexed {len(texts)} records from {table_name}")



from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import os


class VectorStoreService:
    """ChromaDB Vector Store Service with Schema Documentation"""
    
    def __init__(self, persist_directory: str = "./data/vectorstore"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embeddings
        print("Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize ChromaDB
        print("Initializing ChromaDB...")
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="lms_knowledge"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        print("VectorStore initialized successfully!")
    
    def add_schema_documentation(self):
        """Add database schema documentation to vector store"""
        schema_docs = [
            {
                "content": """
                TEACHERS TABLE (teacher_profiles)
                Primary Table: teacher_profiles
                Purpose: Stores all teacher employment and professional information
                
                Key Columns:
                - id: Primary key
                - employee_id_display: Employee ID (e.g., EMP2025-000001)
                - qualification: Teacher's educational qualifications
                - specialization: Subject specialization
                - experience_years: Years of teaching experience
                - designation: Job title/position
                - salary: Current salary
                - is_class_teacher: Boolean indicating if they are a class teacher
                - joining_date: Date teacher joined
                - deleted: Soft delete flag
                
                Related Tables:
                - users: Contains personal info (full_name, email, mobile) linked via user_id
                - employees: Contains employee records linked via employee_id
                
                COMMON QUERIES:
                
                Count all teachers:
                SELECT COUNT(*) as total FROM teacher_profiles WHERE deleted = FALSE
                
                List all teachers:
                SELECT tp.*, u.full_name, u.email, e.employee_id 
                FROM teacher_profiles tp
                LEFT JOIN users u ON tp.user_id = u.id
                LEFT JOIN employees e ON tp.employee_id = e.id
                WHERE tp.deleted = FALSE
                
                Find teachers by specialization:
                SELECT * FROM teacher_profiles 
                WHERE specialization ILIKE '%subject%' AND deleted = FALSE
                
                Teachers with most experience:
                SELECT * FROM teacher_profiles 
                WHERE deleted = FALSE 
                ORDER BY experience_years DESC
                """,
                "metadata": {
                    "type": "schema_documentation",
                    "table": "teacher_profiles",
                    "category": "teachers"
                }
            },
            {
                "content": """
                STUDENTS TABLE
                Primary Table: students
                Purpose: Stores all student enrollment and academic information
                
                COMMON QUERIES:
                
                Count all students:
                SELECT COUNT(*) as total FROM students WHERE deleted = FALSE
                
                Count students by class:
                SELECT class_id, COUNT(*) as total 
                FROM students 
                WHERE deleted = FALSE 
                GROUP BY class_id
                
                List all students:
                SELECT s.*, u.full_name, u.email, c.class_name
                FROM students s
                LEFT JOIN users u ON s.user_id = u.id
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.deleted = FALSE
                """,
                "metadata": {
                    "type": "schema_documentation",
                    "table": "students",
                    "category": "students"
                }
            },
            {
                "content": """
                CLASSES TABLE
                Primary Table: classes
                Purpose: Stores all class/grade information
                
                Related Tables:
                - class_subjects: Links classes with subjects and teachers
                - students: Students enrolled in classes
                
                COMMON QUERIES:
                
                Count all classes:
                SELECT COUNT(*) as total FROM classes WHERE deleted = FALSE
                
                List all classes with student count:
                SELECT c.*, COUNT(s.id) as student_count
                FROM classes c
                LEFT JOIN students s ON c.id = s.class_id AND s.deleted = FALSE
                WHERE c.deleted = FALSE
                GROUP BY c.id
                
                Classes taught by a teacher:
                SELECT c.* FROM classes c
                INNER JOIN class_subjects cs ON c.id = cs.class_id
                WHERE cs.teacher_id = ? AND cs.deleted = FALSE
                """,
                "metadata": {
                    "type": "schema_documentation",
                    "table": "classes",
                    "category": "classes"
                }
            },
            {
                "content": """
                QUERY PATTERNS AND EXAMPLES
                
                Counting Queries:
                - "How many teachers?" → SELECT COUNT(*) FROM teacher_profiles WHERE deleted = FALSE
                - "How many students?" → SELECT COUNT(*) FROM students WHERE deleted = FALSE
                - "How many classes?" → SELECT COUNT(*) FROM classes WHERE deleted = FALSE
                - "Total number of X" → Use COUNT(*) on the main table for entity X
                
                Filtering Queries:
                - "Teachers with experience > 10 years" → WHERE experience_years > 10
                - "Active teachers" → WHERE deleted = FALSE (or status = 'Active' if applicable)
                - "Teachers by specialization" → WHERE specialization ILIKE '%keyword%'
                
                Aggregation Queries:
                - "Average teacher salary" → SELECT AVG(salary) FROM teacher_profiles WHERE deleted = FALSE
                - "Students per class" → GROUP BY class_id with COUNT
                - "Total salary expenditure" → SELECT SUM(salary) FROM teacher_profiles WHERE deleted = FALSE
                
                Important Notes:
                - Always include "deleted = FALSE" in WHERE clauses to exclude soft-deleted records
                - Use ILIKE for case-insensitive text searches in PostgreSQL
                - For counts, use COUNT(*) on the primary entity table, NOT on junction tables
                - class_subjects is a junction table - don't use it for counting teachers/classes
                """,
                "metadata": {
                    "type": "query_patterns",
                    "category": "examples"
                }
            },
            {
                "content": """
                TABLE RELATIONSHIPS
                
                Teacher Relationships:
                teacher_profiles ← (user_id) → users (personal information)
                teacher_profiles ← (employee_id) → employees (employment records)
                teacher_profiles ← (id=teacher_id) → class_subjects (teaching assignments)
                
                Student Relationships:
                students ← (user_id) → users (personal information)
                students ← (class_id) → classes (class enrollment)
                students ← (id=student_id) → attendance (attendance records)
                
                Class Relationships:
                classes ← (id=class_id) → students (enrolled students)
                classes ← (id=class_id) → class_subjects (subjects and teachers)
                
                Important: 
                - class_subjects is a JUNCTION table linking classes, subjects, and teachers
                - DO NOT use class_subjects to count teachers or classes
                - Use the primary entity tables (teacher_profiles, classes) for counts
                """,
                "metadata": {
                    "type": "relationships",
                    "category": "schema"
                }
            }
        ]
        
        # Add schema documentation
        texts = [doc["content"] for doc in schema_docs]
        metadatas = [doc["metadata"] for doc in schema_docs]
        
        self.add_documents(texts, metadatas)
        print(f"Added {len(schema_docs)} schema documentation entries")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """Add documents to vector store"""
        if not texts:
            return
        
        # Split texts into chunks
        chunks = []
        chunk_metadatas = []
        
        for i, text in enumerate(texts):
            if not text or len(text.strip()) == 0:
                continue
            
            # For schema docs, don't split them - keep them whole
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            if metadata.get('type') in ['schema_documentation', 'query_patterns', 'relationships']:
                chunks.append(text)
                chunk_metadatas.append(metadata)
            else:
                # For regular documents, split into chunks
                text_chunks = self.text_splitter.split_text(text)
                chunks.extend(text_chunks)
                chunk_metadatas.extend([metadata] * len(text_chunks))
        
        if chunks:
            # Add to vector store
            self.vectorstore.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas
            )
            print(f"Added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, k: int = 5, filter_metadata: Dict = None) -> List[Dict]:
        """Search similar documents with optional metadata filtering"""
        try:
            # Prioritize schema documentation for query-related searches
            if any(keyword in query.lower() for keyword in ['how many', 'count', 'total', 'list', 'find', 'get']):
                # First try to get schema/pattern docs
                schema_results = self.vectorstore.similarity_search_with_score(
                    query, 
                    k=3,
                    filter={"type": {"$in": ["schema_documentation", "query_patterns", "relationships"]}}
                )
                
                if schema_results:
                    return [
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "score": float(score)
                        }
                        for doc, score in schema_results
                    ]
            
            # Regular search for other queries
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                }
                for doc, score in results
            ]
        except Exception as e:
            print(f"Vector search error: {e}")
            # Fallback to regular search without filter
            try:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
                return [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score)
                    }
                    for doc, score in results
                ]
            except:
                return []
    
    # REMOVED: We don't store actual database records in vector store
    # Vector store is ONLY for schema documentation and query patterns
    # All data queries go directly to PostgreSQL via generated SQL
    
    def initialize_from_extractor(self, schema_docs: List[Dict]):
        """Initialize vector store from extracted schema documents"""
        print(f"Adding {len(schema_docs)} schema documents to vector store...")
        
        texts = [doc["content"] for doc in schema_docs]
        metadatas = [doc["metadata"] for doc in schema_docs]
        
        self.add_documents(texts, metadatas)
        print(f"✓ Added {len(schema_docs)} schema documents to vector store")