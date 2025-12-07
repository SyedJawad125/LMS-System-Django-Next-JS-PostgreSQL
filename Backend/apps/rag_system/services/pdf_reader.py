# import PyPDF2
# try:
#     from docx import Document
#     DOCX_AVAILABLE = True
# except ImportError:
#     DOCX_AVAILABLE = False
#     print("python-docx not installed. DOCX reading will not be available.")


# class DocumentReader:
#     """Read and extract text from documents"""
    
#     @staticmethod
#     def read_pdf(file_path: str) -> str:
#         """Extract text from PDF"""
#         try:
#             with open(file_path, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 text = ""
#                 for page in pdf_reader.pages:
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
#                 return text.strip()
#         except Exception as e:
#             print(f"Error reading PDF: {e}")
#             return ""
    
#     @staticmethod
#     def read_docx(file_path: str) -> str:
#         """Extract text from Word document"""
#         if not DOCX_AVAILABLE:
#             print("python-docx not installed")
#             return ""
        
#         try:
#             doc = Document(file_path)
#             text = "\n".join([para.text for para in doc.paragraphs if para.text])
#             return text.strip()
#         except Exception as e:
#             print(f"Error reading DOCX: {e}")
#             return ""
    
#     @staticmethod
#     def read_txt(file_path: str) -> str:
#         """Read text file"""
#         try:
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 return file.read().strip()
#         except Exception as e:
#             print(f"Error reading TXT: {e}")
#             return ""
    
#     @classmethod
#     def read_document(cls, file_path: str, doc_type: str) -> str:
#         """Read document based on type"""
#         if doc_type == 'pdf':
#             return cls.read_pdf(file_path)
#         elif doc_type == 'docx':
#             return cls.read_docx(file_path)
#         elif doc_type in ['txt', 'csv']:
#             return cls.read_txt(file_path)
#         else:
#             print(f"Unsupported document type: {doc_type}")
#             return ""


# ============================================
# FILE 10: apps/rag_system/services/pdf_reader.py
# ============================================

import PyPDF2
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx not installed. DOCX reading will not be available.")


class DocumentReader:
    """Read and extract text from documents"""
    
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    @staticmethod
    def read_docx(file_path: str) -> str:
        """Extract text from Word document"""
        if not DOCX_AVAILABLE:
            print("python-docx not installed")
            return ""
        
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
            return text.strip()
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""
    
    @staticmethod
    def read_txt(file_path: str) -> str:
        """Read text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    
    @classmethod
    def read_document(cls, file_path: str, doc_type: str) -> str:
        """Read document based on type"""
        if doc_type == 'pdf':
            return cls.read_pdf(file_path)
        elif doc_type == 'docx':
            return cls.read_docx(file_path)
        elif doc_type in ['txt', 'csv']:
            return cls.read_txt(file_path)
        else:
            print(f"Unsupported document type: {doc_type}")
            return ""