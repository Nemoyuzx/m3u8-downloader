from django.db import models
from django.utils import timezone
import uuid


class DownloadTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('merging', 'Merging'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0.0)  # 0-100
    file_size = models.BigIntegerField(null=True, blank=True)
    downloaded_size = models.BigIntegerField(default=0)
    speed = models.CharField(max_length=50, blank=True)  # e.g., "1.5 MB/s"
    eta = models.CharField(max_length=50, blank=True)  # e.g., "5m 30s"
    
    # Segment information
    total_segments = models.IntegerField(default=0)
    downloaded_segments = models.IntegerField(default=0)
    failed_segments = models.IntegerField(default=0)
    
    # File paths
    output_path = models.CharField(max_length=1000, blank=True)
    temp_dir = models.CharField(max_length=1000, blank=True)
    
    # Additional metadata
    headers = models.JSONField(default=dict, blank=True)
    encryption_key = models.TextField(blank=True)
    encryption_iv = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error information
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.status}"


class DownloadSegment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    task = models.ForeignKey(DownloadTask, on_delete=models.CASCADE, related_name='segments')
    index = models.IntegerField()
    url = models.URLField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=1000, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['index']
        unique_together = ['task', 'index']
    
    def __str__(self):
        return f"Segment {self.index} of {self.task.title or 'Untitled'}"
