# from rest_framework import serializers
# from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics


# class DocumentStoreSerializer(serializers.ModelSerializer):
#     uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
#     class Meta:
#         model = DocumentStore
#         fields = [
#             'id', 'title', 'document_type', 'file', 
#             'uploaded_by', 'uploaded_by_username', 'uploaded_at',
#             'is_processed', 'vector_count', 'metadata'
#         ]
#         read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'is_processed', 'vector_count']


# class ChatQuerySerializer(serializers.Serializer):
#     query = serializers.CharField(max_length=5000, required=True)
#     session_id = serializers.CharField(max_length=100, required=False)
#     use_cache = serializers.BooleanField(default=True)


# class ChatResponseSerializer(serializers.Serializer):
#     query = serializers.CharField()
#     response = serializers.CharField()
#     context_sources = serializers.DictField()
#     tokens_used = serializers.IntegerField()
#     response_time = serializers.FloatField()
#     success = serializers.BooleanField()
#     cached = serializers.BooleanField(default=False)


# class ChatHistorySerializer(serializers.ModelSerializer):
#     user_username = serializers.CharField(source='user.username', read_only=True)
    
#     class Meta:
#         model = ChatHistory
#         fields = [
#             'id', 'user', 'user_username', 'session_id',
#             'query', 'response', 'context_used', 'sql_queries',
#             'tokens_used', 'response_time', 'created_at'
#         ]
#         read_only_fields = ['id', 'user', 'created_at']


# class QueryCacheSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QueryCache
#         fields = '__all__'
#         read_only_fields = ['query_hash', 'created_at', 'last_used']


# class RAGMetricsSerializer(serializers.ModelSerializer):
#     success_rate = serializers.SerializerMethodField()
    
#     class Meta:
#         model = RAGMetrics
#         fields = [
#             'date', 'total_queries', 'successful_queries',
#             'failed_queries', 'success_rate', 'avg_response_time',
#             'total_tokens_used', 'cache_hit_rate'
#         ]
    
#     def get_success_rate(self, obj):
#         if obj.total_queries > 0:
#             return round((obj.successful_queries / obj.total_queries) * 100, 2)
#         return 0.0

# ============================================
# FILE 5: apps/rag_system/serializers.py
# ============================================

from rest_framework import serializers
from .models import DocumentStore, ChatHistory, QueryCache, RAGMetrics


class DocumentStoreSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = DocumentStore
        fields = [
            'id', 'title', 'document_type', 'file', 
            'uploaded_by', 'uploaded_by_username', 'uploaded_at',
            'is_processed', 'vector_count', 'metadata'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'is_processed', 'vector_count']


class ChatQuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=5000, required=True)
    session_id = serializers.CharField(max_length=100, required=False)
    use_cache = serializers.BooleanField(default=True)


class ChatResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    response = serializers.CharField()
    context_sources = serializers.DictField()
    tokens_used = serializers.IntegerField()
    response_time = serializers.FloatField()
    success = serializers.BooleanField()
    cached = serializers.BooleanField(default=False)


class ChatHistorySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatHistory
        fields = [
            'id', 'user', 'user_username', 'session_id',
            'query', 'response', 'context_used', 'sql_queries',
            'tokens_used', 'response_time', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class QueryCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryCache
        fields = '__all__'
        read_only_fields = ['query_hash', 'created_at', 'last_used']


class RAGMetricsSerializer(serializers.ModelSerializer):
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = RAGMetrics
        fields = [
            'date', 'total_queries', 'successful_queries',
            'failed_queries', 'success_rate', 'avg_response_time',
            'total_tokens_used', 'cache_hit_rate'
        ]
    
    def get_success_rate(self, obj):
        if obj.total_queries > 0:
            return round((obj.successful_queries / obj.total_queries) * 100, 2)
        return 0.0