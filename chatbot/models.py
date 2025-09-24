from django.db import models
from django.conf import settings
import uuid


class CSVFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='csv_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'CSV File'
        verbose_name_plural = 'CSV Files'

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='chat_sessions'
    )
    # For anonymous users, we'll use session_key
    session_key = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['session_key', '-updated_at']),
        ]

    def __str__(self):
        if self.user:
            return f"Session by {self.user.email} - {self.title or 'Untitled'}"
        return f"Anonymous Session - {self.title or 'Untitled'}"

    def save(self, *args, **kwargs):
        # Auto-generate title from first message if not provided
        if not self.title and self.messages.exists():
            first_message = self.messages.filter(role='user').first()
            if first_message:
                self.title = (first_message.content[:50] + '...') if len(first_message.content) > 50 else first_message.content
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    location = models.CharField(max_length=500, blank=True, null=True)  # User location if provided
    keywords = models.JSONField(default=list, blank=True)  # Extracted keywords
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Metadata for tracking
    response_time = models.FloatField(null=True, blank=True)  # Response time in seconds
    context_used = models.BooleanField(default=False)  # Whether CSV context was used

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['role', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.role.capitalize()}: {self.content[:100]}..."
