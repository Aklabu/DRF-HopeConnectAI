import uuid
from django.db import models
from django.utils import timezone


class Alert(models.Model):
    """
    Weather Alert model to store weather alerts from National Weather Service API
    """
    SEVERITY_CHOICES = [
        ('Minor', 'Minor'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
        ('Extreme', 'Extreme'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_id = models.CharField(max_length=500, unique=True, help_text="Unique ID from NWS API")
    event = models.CharField(max_length=200, help_text="Type of weather event")
    headline = models.CharField(max_length=500, help_text="Alert headline")
    description = models.TextField(help_text="Detailed alert description")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, help_text="Alert severity level")
    area = models.CharField(max_length=500, help_text="Geographic area description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_id']),
            models.Index(fields=['severity']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.event} - {self.area} ({self.severity})"