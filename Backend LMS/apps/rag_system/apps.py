# from django.apps import AppConfig


# class RagSystemConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'rag_system'



# from django.apps import AppConfig


# class RagSystemConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'apps.rag_system'
#     verbose_name = 'RAG System'
    
#     def ready(self):
#         """Initialize when Django starts"""
#         pass

# ============================================
# FILE 2: apps/rag_system/apps.py
# ============================================

from django.apps import AppConfig


class RagSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rag_system'
    verbose_name = 'RAG System'
    
    def ready(self):
        """Initialize when Django starts"""
        pass



