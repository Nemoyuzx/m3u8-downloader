from django.db import models
from django.utils import timezone


class TaskHistory(models.Model):
    ACTION_CHOICES = [
        ('download_started', 'Download Started'),
        ('download_completed', 'Download Completed'),
        ('download_failed', 'Download Failed'),
        ('download_paused', 'Download Paused'),
        ('download_resumed', 'Download Resumed'),
        ('download_cancelled', 'Download Cancelled'),
        ('file_deleted', 'File Deleted'),
        ('file_moved', 'File Moved'),
        ('merge_started', 'Merge Started'),
        ('merge_completed', 'Merge Completed'),
        ('merge_failed', 'Merge Failed'),
    ]
    
    task_id = models.UUIDField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.task_id}"


class SystemLog(models.Model):
    LOG_LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=20, choices=LOG_LEVEL_CHOICES, default='INFO')
    message = models.TextField()
    module = models.CharField(max_length=100, blank=True)
    function = models.CharField(max_length=100, blank=True)
    line_number = models.IntegerField(null=True, blank=True)
    
    # Additional context
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.level}] {self.message[:50]}..."
