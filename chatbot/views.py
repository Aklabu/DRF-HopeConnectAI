from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.db.models import Count, Avg
from django.utils import timezone
from utils.response import CustomResponse
import pandas as pd
import time
import os
import re

from .models import CSVFile, ChatSession, ChatMessage
from .serializers import (
    CSVFileSerializer, ChatSessionSerializer, ChatSessionListSerializer,
    ChatMessageSerializer, ChatRequestSerializer, ChatResponseSerializer, SessionStatsSerializer
)
from .utils.file_uploder import file_uploder
from .utils.pipeline import HopePipeline

class ChatView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ChatRequestSerializer

    def __init__(self):
        super().__init__()
        self.pipeline = HopePipeline(api_key=settings.OPENAI_API_KEY)
        self.csv_data = self.load_csv_data()

    def load_csv_data(self):
        """Load the active CSV data"""
        try:
            active_csv = CSVFile.objects.filter(is_active=True).first()
            if active_csv and active_csv.file:
                return pd.read_csv(active_csv.file.path)
        except Exception as e:
            print(f"Error loading CSV data: {e}")
        return None

    def get_or_create_session(self, user, session_id, session_key):
        """Get existing session or create new one"""
        if session_id:
            try:
                if user and user.is_authenticated:
                    session = ChatSession.objects.get(id=session_id, user=user)
                else:
                    session = ChatSession.objects.get(id=session_id, session_key=session_key)
                return session
            except ChatSession.DoesNotExist:
                pass

        # Create new session
        session_data = {'is_active': True}
        if user and user.is_authenticated:
            session_data['user'] = user
        else:
            session_data['session_key'] = session_key

        return ChatSession.objects.create(**session_data)

    def build_history(self, session):
        """Build conversation history for the pipeline"""
        messages = session.messages.filter(role__in=['user', 'assistant']).order_by('timestamp')
        history = []
        for msg in messages:
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        return history

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']
        location = serializer.validated_data.get('location', '')
        session_id = serializer.validated_data.get('session_id')

        # Get or generate session key for anonymous users
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Get or create session
        session = self.get_or_create_session(
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id,
            session_key=session_key
        )

        # Build conversation history
        history = self.build_history(session)

        # Extract keywords before processing
        keywords = file_uploder.extract_keywords(user_message)

        start_time = time.time()

        try:
            # Get response from pipeline
            response = self.pipeline.run(
                user_input=user_message,
                location=location,
                csv_data=self.csv_data,
                history=history
            )

            response_time = time.time() - start_time
            context_used = bool(self.csv_data is not None and keywords)

            # Save user message
            user_msg = ChatMessage.objects.create(
                session=session,
                role='user',
                content=user_message,
                location=location,
                keywords=keywords,
                context_used=context_used
            )

            # Save assistant response
            assistant_msg = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=response,
                keywords=keywords,
                context_used=context_used,
                response_time=response_time
            )

            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()

            # Prepare response
            response_data = {
                'response': response,
                'session_id': str(session.id),
                'keywords': keywords,
                'context_used': context_used,
                'response_time': round(response_time, 2)
            }

            return CustomResponse.success("Message processed successfully", response_data)

        except Exception as e:
            return CustomResponse.error(f"Error processing message: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ChatSessionListView(generics.ListAPIView):
    serializer_class = ChatSessionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related('messages')


class ChatSessionDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related('messages')


class ChatSessionDeleteView(generics.DestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user,
            is_active=True
        )

    def delete(self, request, *args, **kwargs):
        session = self.get_object()
        session.is_active = False
        session.save()
        return CustomResponse.success("Chat session deleted successfully")


class CSVFileListView(generics.ListAPIView):
    serializer_class = CSVFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CSVFile.objects.all().order_by('-uploaded_at')
        return CSVFile.objects.none()


class ReloadCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_staff:
            return CustomResponse.error("Permission denied", status.HTTP_403_FORBIDDEN)
        
        # This endpoint can be used to reload CSV data in the chat service
        # For now, we'll just return success as the CSV is loaded per request
        return CustomResponse.success("CSV data reloaded successfully")
