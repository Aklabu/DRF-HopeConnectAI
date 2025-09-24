from django.urls import path
from .views import (
    ChatView,
    ChatSessionListView,
    ChatSessionDetailView,
    ChatSessionDeleteView,
)

app_name = 'chatbot'

urlpatterns = [
    # Chat endpoints
    path('chat/', ChatView.as_view(), name='chat'),
    
    # Session management (for authenticated users)
    path('sessions/', ChatSessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:pk>/', ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:pk>/delete/', ChatSessionDeleteView.as_view(), name='session-delete'),
]