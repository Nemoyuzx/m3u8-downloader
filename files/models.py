from django.db import models
from django.utils import timezone
import os


class DownloadedFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]
    
    filename = models.CharField(max_length=500)
    original_name = models.CharField(max_length=500, blank=True)
    file_path = models.CharField(max_length=1000)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='video')
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Metadata
    duration = models.CharField(max_length=50, blank=True)  # e.g., "01:30:45"
    resolution = models.CharField(max_length=20, blank=True)  # e.g., "1920x1080"
    format = models.CharField(max_length=20, blank=True)  # e.g., "mp4", "ts"
    
    # Related task
    download_task_id = models.UUIDField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename
    
    @property
    def file_size_formatted(self):
        """Return formatted file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 ** 2:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 ** 3:
            return f"{self.file_size / (1024 ** 2):.1f} MB"
        else:
            return f"{self.file_size / (1024 ** 3):.1f} GB"
    
    def delete_file(self):
        """Delete the actual file from disk"""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            return True
        return False
