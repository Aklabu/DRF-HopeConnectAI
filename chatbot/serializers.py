from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CSVFile, ChatSession, ChatMessage


class CSVFileSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)

    class Meta:
        model = CSVFile
        fields = [
            'id', 'name', 'file', 'description', 'is_active', 
            'uploaded_at', 'uploaded_by_email', 'file_size'
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_email']

    def get_file_size(self, obj):
        if obj.file:
            try:
                size = obj.file.size
                if size < 1024:
                    return f"{size} bytes"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except:
                return "Unknown"
        return "No file"


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'content', 'location', 'keywords', 
            'timestamp', 'context_used', 'response_time'
        ]
        read_only_fields = [
            'id', 'timestamp', 'keywords', 'context_used', 'response_time'
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'user_email', 'session_key', 'created_at', 
            'updated_at', 'is_active', 'message_count', 'messages'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'user_email', 'message_count'
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatSessionListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'user_email', 'created_at', 'updated_at', 
            'is_active', 'message_count', 'last_message'
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_message_count(self, obj):
        return obj.messages.count()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': (last_msg.content[:100] + '...') if len(last_msg.content) > 100 else last_msg.content,
                'role': last_msg.role,
                'timestamp': last_msg.timestamp
            }
        return None


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=5000)
    location = serializers.CharField(max_length=500, required=False, allow_blank=True)
    session_id = serializers.UUIDField(required=False)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    session_id = serializers.UUIDField()
    keywords = serializers.ListField(child=serializers.CharField())
    context_used = serializers.BooleanField()
    response_time = serializers.FloatField()


class SessionStatsSerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    average_messages_per_session = serializers.FloatField()
    user_sessions = serializers.IntegerField()
    anonymous_sessions = serializers.IntegerField()