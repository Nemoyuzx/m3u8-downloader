from django.contrib import admin
from .models import DownloadedFile


@admin.register(DownloadedFile)
class DownloadedFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file_type', 'file_size_formatted', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['filename', 'original_name']
    readonly_fields = ['created_at', 'modified_at', 'file_size_formatted']
    
    fieldsets = (
        ('File Info', {
            'fields': ('filename', 'original_name', 'file_path', 'file_type', 'mime_type')
        }),
        ('Size & Format', {
            'fields': ('file_size', 'file_size_formatted', 'duration', 'resolution', 'format')
        }),
        ('Related Task', {
            'fields': ('download_task_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at')
        })
    )
