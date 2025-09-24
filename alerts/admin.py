from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """
    Admin interface for Alert model
    """
    list_display = ['event', 'severity', 'area', 'created_at']
    list_filter = ['severity', 'created_at']
    search_fields = ['event', 'headline', 'area']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('source_id', 'event', 'headline', 'severity', 'area')
        }),
        ('Content', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
