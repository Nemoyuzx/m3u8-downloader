from django.contrib import admin
from .models import TaskHistory, SystemLog


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'action', 'description', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['task_id', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Task Info', {
            'fields': ('task_id', 'action', 'description')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message', 'module', 'function', 'created_at']
    list_filter = ['level', 'module', 'created_at']
    search_fields = ['message', 'module', 'function']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Log Info', {
            'fields': ('level', 'message')
        }),
        ('Source', {
            'fields': ('module', 'function', 'line_number')
        }),
        ('Extra Data', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
