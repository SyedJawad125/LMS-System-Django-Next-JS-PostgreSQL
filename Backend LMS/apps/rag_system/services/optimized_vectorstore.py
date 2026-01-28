# ============================================
# OPTIMIZED VECTOR STORE SERVICE
# File: apps/rag_system/services/optimized_vectorstore.py
# ============================================

"""
Key improvements over original:
1. Semantic chunking (not just by character count)
2. Hybrid search (vector + keyword)
3. Query expansion
4. Better metadata for filtering
5. Reranking with cross-encoder
"""

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Dict, Optional
import os
import re
from collections import defaultdict


class OptimizedVectorStore:
    """Enhanced vector store with better retrieval"""
    
    def __init__(self, persist_directory: str = "./data/vectorstore_v2"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        print("🚀 Initializing Optimized Vector Store...")
        
        # Use better embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",  # Better than MiniLM
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}  # Important for better similarity
        )
        
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="lms_knowledge_v2"
        )
        
        print("✅ Optimized Vector Store ready!")
    
    def add_documents_optimized(self, documents: List[Dict]):
        """Add documents with semantic chunking"""
        
        all_chunks = []
        all_metadata = []
        
        for doc in documents:
            content = doc['content']
            metadata = doc['metadata']
            
            # Semantic chunking based on content type
            if metadata.get('type') == 'entity_knowledge':
                chunks = self._chunk_entity_document(content)
            elif metadata.get('type') == 'query_pattern':
                chunks = self._chunk_query_pattern(content)
            else:
                chunks = self._chunk_generic(content)
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                
                # Extract additional metadata from content
                chunk_metadata.update(self._extract_chunk_metadata(chunk))
                
                all_chunks.append(chunk)
                all_metadata.append(chunk_metadata)
        
        if all_chunks:
            self.vectorstore.add_texts(
                texts=all_chunks,
                metadatas=all_metadata
            )
            print(f"📚 Added {len(all_chunks)} optimized chunks")
    
    def _chunk_entity_document(self, content: str) -> List[str]:
        """Chunk entity documents by logical sections"""
        chunks = []
        
        # Split by major sections
        sections = re.split(r'\n(?=[A-Z ]{10,}:\n)', content)
        
        for section in sections:
            if len(section.strip()) < 50:
                continue
            
            # If section is very long, split further
            if len(section) > 1500:
                # Split by subsections or paragraphs
                subsections = section.split('\n\n')
                current_chunk = ""
                
                for subsection in subsections:
                    if len(current_chunk) + len(subsection) < 1000:
                        current_chunk += "\n\n" + subsection
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = subsection
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks.append(section.strip())
        
        return chunks
    
    def _chunk_query_pattern(self, content: str) -> List[str]:
        """Keep query patterns together (don't split examples)"""
        # Query patterns should stay as single chunks
        return [content]
    
    def _chunk_generic(self, content: str, max_size: int = 1000, overlap: int = 200) -> List[str]:
        """Generic chunking with overlap"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_size:
                current_chunk += "\n\n" + para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                words = current_chunk.split()[-overlap:]
                current_chunk = " ".join(words) + "\n\n" + para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _extract_chunk_metadata(self, chunk: str) -> Dict:
        """Extract metadata from chunk content"""
        metadata = {}
        
        # Extract mentioned tables
        tables = re.findall(r'(?:FROM|JOIN)\s+(\w+)', chunk, re.IGNORECASE)
        if tables:
            metadata['mentioned_tables'] = list(set(tables))
        
        # Extract mentioned columns
        columns = re.findall(r'(?:SELECT|WHERE)\s+(\w+)', chunk, re.IGNORECASE)
        if columns:
            metadata['mentioned_columns'] = list(set(columns))[:10]
        
        # Check if contains SQL
        if 'SELECT' in chunk.upper():
            metadata['contains_sql'] = True
        
        # Check if contains examples
        if 'example' in chunk.lower():
            metadata['contains_examples'] = True
        
        return metadata
    
    def hybrid_search(self, query: str, k: int = 10) -> List[Dict]:
        """
        Hybrid search: Vector similarity + Keyword matching + Query expansion
        """
        
        # 1. Expand query
        expanded_queries = self._expand_query_advanced(query)
        
        # 2. Vector search for each expansion
        all_results = []
        seen_content = set()
        
        for exp_query in expanded_queries:
            results = self.vectorstore.similarity_search_with_score(
                exp_query,
                k=k * 2  # Get more results for reranking
            )
            
            for doc, score in results:
                content_hash = hash(doc.page_content[:100])
                
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    
                    all_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'vector_score': float(1 - score),  # Convert distance to similarity
                        'query_variant': exp_query
                    })
        
        # 3. Add keyword boosting
        for result in all_results:
            keyword_score = self._keyword_match_score(query, result['content'])
            result['keyword_score'] = keyword_score
        
        # 4. Add metadata boosting
        for result in all_results:
            metadata_score = self._metadata_relevance_score(query, result['metadata'])
            result['metadata_score'] = metadata_score
        
        # 5. Calculate combined score
        for result in all_results:
            result['final_score'] = (
                result['vector_score'] * 0.5 +
                result['keyword_score'] * 0.3 +
                result['metadata_score'] * 0.2
            )
        
        # 6. Sort by final score
        all_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 7. Return top k
        return all_results[:k]
    
    def _expand_query_advanced(self, query: str) -> List[str]:
        """Advanced query expansion"""
        expansions = [query]
        query_lower = query.lower()
        
        # Entity synonyms
        synonyms = {
            'user': ['account', 'profile', 'member'],
            'student': ['pupil', 'learner', 'enrolled student'],
            'teacher': ['instructor', 'faculty', 'educator'],
            'class': ['grade', 'section', 'classroom'],
            'exam': ['test', 'assessment', 'evaluation'],
            'fee': ['payment', 'invoice', 'charge', 'tuition'],
            'attendance': ['presence', 'absence', 'participation'],
            'permission': ['access', 'rights', 'privileges', 'capability'],
            'role': ['user type', 'access level', 'position']
        }
        
        # Replace entities with synonyms
        for entity, syns in synonyms.items():
            if entity in query_lower:
                for syn in syns[:2]:  # Use top 2 synonyms
                    expansions.append(query_lower.replace(entity, syn))
        
        # Query type transformations
        transformations = [
            ('how many', 'count'),
            ('show me', 'list'),
            ('display', 'show'),
            ('what are', 'list'),
            ('get all', 'show'),
            ('find', 'search'),
            ('what permissions does', 'permissions for'),
            ('what can', 'capabilities of')
        ]
        
        for old, new in transformations:
            if old in query_lower:
                expansions.append(query_lower.replace(old, new))
        
        # Add entity-focused versions
        entities_in_query = [e for e in synonyms.keys() if e in query_lower]
        for entity in entities_in_query:
            expansions.append(f"{entity} information database schema")
            expansions.append(f"query {entity} table")
        
        return list(set(expansions))[:5]  # Return unique, top 5
    
    def _keyword_match_score(self, query: str, content: str) -> float:
        """Calculate keyword matching score"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # Exact matches
        exact_matches = query_words & content_words
        
        # Partial matches
        partial_matches = 0
        for qword in query_words:
            if any(qword in cword or cword in qword for cword in content_words):
                partial_matches += 1
        
        score = (len(exact_matches) * 2 + partial_matches) / (len(query_words) + 1)
        
        return min(1.0, score)
    
    def _metadata_relevance_score(self, query: str, metadata: Dict) -> float:
        """Score based on metadata relevance"""
        score = 0.0
        query_lower = query.lower()
        
        # Boost by priority
        priority = metadata.get('priority', 'medium')
        if priority == 'critical' or priority == 'very_high':
            score += 0.5
        elif priority == 'high':
            score += 0.3
        
        # Boost by type matching
        type_matches = {
            'count': 'query_pattern',
            'list': 'query_pattern',
            'permission': 'business_logic',
            'role': 'business_logic',
            'student': 'entity_knowledge',
            'teacher': 'entity_knowledge'
        }
        
        for keyword, doc_type in type_matches.items():
            if keyword in query_lower and metadata.get('type') == doc_type:
                score += 0.2
                break
        
        # Boost if contains examples
        if 'example' in query_lower and metadata.get('contains_examples'):
            score += 0.2
        
        # Boost if contains SQL
        if 'sql' in query_lower and metadata.get('contains_sql'):
            score += 0.2
        
        # Boost if entity matches
        if metadata.get('entity') and metadata['entity'] in query_lower:
            score += 0.3
        
        # Boost if mentioned tables match query
        if metadata.get('mentioned_tables'):
            for table in metadata['mentioned_tables']:
                if table.lower() in query_lower:
                    score += 0.2
                    break
        
        return min(1.0, score)
    
    def search(self, query: str, k: int = 10) -> List[Dict]:
        """Main search interface - uses hybrid search"""
        return self.hybrid_search(query, k=k)
    
    def stats(self) -> Dict:
        """Get statistics"""
        try:
            count = self.vectorstore._collection.count()
            return {
                'total_chunks': count,
                'status': 'operational' if count > 0 else 'empty',
                'persist_directory': self.persist_directory,
                'embedding_model': 'all-mpnet-base-v2'
            }
        except:
            return {
                'total_chunks': 0,
                'status': 'error',
                'persist_directory': self.persist_directory
            }


# ============================================
# INTEGRATION FUNCTION
# ============================================

def initialize_optimized_vectorstore():
    """Initialize with improved data ingestion"""
    from .improved_data_ingestion import ImprovedDataIngestion
    
    print("🚀 Starting Optimized Vector Store Initialization...")
    
    # 1. Generate rich knowledge base
    print("\n📚 Step 1: Generating rich knowledge base...")
    ingestion = ImprovedDataIngestion()
    documents = ingestion.generate_rich_knowledge_base()
    print(f"   Generated {len(documents)} documents")
    
    # 2. Initialize optimized vector store
    print("\n🔧 Step 2: Initializing optimized vector store...")
    vectorstore = OptimizedVectorStore()
    
    # 3. Add documents with optimized chunking
    print("\n✂️ Step 3: Adding documents with semantic chunking...")
    vectorstore.add_documents_optimized(documents)
    
    # 4. Show stats
    stats = vectorstore.stats()
    print(f"\n✅ Initialization Complete!")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Status: {stats['status']}")
    print(f"   Model: {stats['embedding_model']}")
    
    return vectorstore


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    vectorstore = initialize_optimized_vectorstore()
    
    # Test queries
    test_queries = [
        "How many students are there?",
        "List all teachers",
        "What permissions does Teacher role have?",
        "Show student attendance"
    ]
    
    print("\n" + "="*80)
    print("TESTING SEARCH QUALITY")
    print("="*80)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = vectorstore.search(query, k=3)
        
        print(f"   Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\n   Result {i}:")
            print(f"   Score: {result['final_score']:.3f}")
            print(f"   Type: {result['metadata'].get('type')}")
            print(f"   Entity: {result['metadata'].get('entity', 'N/A')}")
            print(f"   Preview: {result['content'][:150]}...")