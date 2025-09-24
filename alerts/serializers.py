from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert model
    """
    class Meta:
        model = Alert
        fields = [
            'id', 'source_id', 'event', 'headline', 
            'description', 'severity', 'area', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']