# from django.contrib import admin

# # Register your models here.

# from django.contrib import admin
# from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics


# @admin.register(DocumentStore)
# class DocumentStoreAdmin(admin.ModelAdmin):
#     list_display = ['title', 'document_type', 'uploaded_by', 'is_processed', 'uploaded_at']
#     list_filter = ['document_type', 'is_processed', 'uploaded_at']
#     search_fields = ['title', 'uploaded_by__username']
#     readonly_fields = ['uploaded_at', 'vector_count', 'id']
    
#     fieldsets = (
#         ('Document Info', {
#             'fields': ('id', 'title', 'document_type', 'file')
#         }),
#         ('Processing', {
#             'fields': ('is_processed', 'vector_count', 'metadata')
#         }),
#         ('Tracking', {
#             'fields': ('uploaded_by', 'uploaded_at')
#         }),
#     )


# @admin.register(ChatHistory)
# class ChatHistoryAdmin(admin.ModelAdmin):
#     list_display = ['user', 'short_query', 'session_id', 'tokens_used', 'response_time', 'created_at']
#     list_filter = ['user', 'created_at']
#     search_fields = ['query', 'response', 'user__username', 'session_id']
#     readonly_fields = ['created_at', 'id']
#     date_hierarchy = 'created_at'
    
#     def short_query(self, obj):
#         return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
#     short_query.short_description = 'Query'


# @admin.register(QueryCache)
# class QueryCacheAdmin(admin.ModelAdmin):
#     list_display = ['short_query', 'hit_count', 'last_used', 'created_at']
#     list_filter = ['created_at', 'last_used']
#     search_fields = ['query_text', 'response']
#     readonly_fields = ['query_hash', 'created_at', 'last_used']
#     ordering = ['-hit_count']
    
#     def short_query(self, obj):
#         return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
#     short_query.short_description = 'Query'


# @admin.register(RAGMetrics)
# class RAGMetricsAdmin(admin.ModelAdmin):
#     list_display = [
#         'date', 'total_queries', 'successful_queries', 
#         'failed_queries', 'avg_response_time', 'cache_hit_rate'
#     ]
#     list_filter = ['date']
#     readonly_fields = ['date']
#     date_hierarchy = 'date'


from django.contrib import admin
from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics


@admin.register(DocumentStore)
class DocumentStoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'uploaded_by', 'is_processed', 'uploaded_at']
    list_filter = ['document_type', 'is_processed', 'uploaded_at']
    search_fields = ['title', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'vector_count', 'id']
    
    fieldsets = (
        ('Document Info', {
            'fields': ('id', 'title', 'document_type', 'file')
        }),
        ('Processing', {
            'fields': ('is_processed', 'vector_count', 'metadata')
        }),
        ('Tracking', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_query', 'session_id', 'tokens_used', 'response_time', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['query', 'response', 'user__username', 'session_id']
    readonly_fields = ['created_at', 'id']
    date_hierarchy = 'created_at'
    
    def short_query(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    short_query.short_description = 'Query'


@admin.register(QueryCache)
class QueryCacheAdmin(admin.ModelAdmin):
    list_display = ['short_query', 'hit_count', 'last_used', 'created_at']
    list_filter = ['created_at', 'last_used']
    search_fields = ['query_text', 'response']
    readonly_fields = ['query_hash', 'created_at', 'last_used']
    ordering = ['-hit_count']
    
    def short_query(self, obj):
        return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
    short_query.short_description = 'Query'


@admin.register(RAGMetrics)
class RAGMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_queries', 'successful_queries', 
        'failed_queries', 'avg_response_time', 'cache_hit_rate'
    ]
    list_filter = ['date']
    readonly_fields = ['date']
    date_hierarchy = 'date'