from django.contrib import admin
from .models import DownloadTask, DownloadSegment


@admin.register(DownloadTask)
class DownloadTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'progress', 'total_segments', 'downloaded_segments', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'url']
    readonly_fields = ['id', 'created_at', 'started_at', 'completed_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'url', 'title', 'status')
        }),
        ('Progress', {
            'fields': ('progress', 'total_segments', 'downloaded_segments', 'failed_segments')
        }),
        ('File Info', {
            'fields': ('file_size', 'downloaded_size', 'speed', 'eta', 'output_path', 'temp_dir')
        }),
        ('Encryption', {
            'fields': ('encryption_key', 'encryption_iv'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
        ('Error Info', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )


@admin.register(DownloadSegment)
class DownloadSegmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'index', 'status', 'file_size', 'retry_count', 'created_at']
    list_filter = ['status', 'task__title']
    search_fields = ['task__title', 'url']
    readonly_fields = ['created_at', 'completed_at']
