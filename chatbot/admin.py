from django.contrib import admin
from django.utils.html import format_html
from .models import CSVFile


@admin.register(CSVFile)
class CSVFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'uploaded_at', 'uploaded_by', 'file_size']
    list_filter = ['is_active', 'uploaded_at', 'uploaded_by']
    search_fields = ['name', 'description']
    readonly_fields = ['uploaded_at', 'file_size_display']
    fieldsets = (
        (None, {
            'fields': ('name', 'file', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'uploaded_by', 'file_size_display'),
            'classes': ('collapse',)
        }),
    )

    def file_size(self, obj):
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
    file_size.short_description = "File Size"

    def file_size_display(self, obj):
        return self.file_size(obj)
    file_size_display.short_description = "File Size"

    def save_model(self, request, obj, form, change):
        if not change:  # creating new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    # 🚨 Prevent multiple uploads
    def has_add_permission(self, request):
        # Allow adding only if no CSVFile exists
        if CSVFile.objects.exists():
            return False
        return super().has_add_permission(request)


