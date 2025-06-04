from rest_framework import serializers
from .models import DownloadTask, DownloadSegment


class DownloadSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadSegment
        fields = ['index', 'url', 'status', 'file_size', 'retry_count', 'error_message', 'created_at', 'completed_at']


class DownloadTaskSerializer(serializers.ModelSerializer):
    segments = DownloadSegmentSerializer(many=True, read_only=True)
    file_size_formatted = serializers.SerializerMethodField()
    downloaded_size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = DownloadTask
        fields = [
            'id', 'url', 'title', 'status', 'progress', 'file_size', 'downloaded_size',
            'speed', 'eta', 'total_segments', 'downloaded_segments', 'failed_segments',
            'output_path', 'created_at', 'started_at', 'completed_at', 'error_message',
            'segments', 'file_size_formatted', 'downloaded_size_formatted'
        ]
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']
    
    def get_file_size_formatted(self, obj):
        if not obj.file_size:
            return "Unknown"
        return self._format_size(obj.file_size)
    
    def get_downloaded_size_formatted(self, obj):
        return self._format_size(obj.downloaded_size)
    
    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.1f} MB"
        else:
            return f"{size / (1024 ** 3):.1f} GB"


class DownloadTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadTask
        fields = ['url', 'title', 'headers', 'output_path']
    
    def validate_url(self, value):
        if not value.strip():
            raise serializers.ValidationError("URL cannot be empty")
        if not (value.startswith('http://') or value.startswith('https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value


class DownloadTaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadTask
        fields = ['status', 'title']
    
    def validate_status(self, value):
        allowed_transitions = {
            'pending': ['downloading', 'cancelled'],
            'downloading': ['paused', 'cancelled', 'failed', 'merging'],
            'paused': ['downloading', 'cancelled'],
            'merging': ['completed', 'failed'],
            'failed': ['downloading'],
            'completed': [],
            'cancelled': ['downloading']
        }
        
        instance = self.instance
        if instance and instance.status in allowed_transitions:
            if value not in allowed_transitions[instance.status]:
                raise serializers.ValidationError(
                    f"Cannot transition from {instance.status} to {value}"
                )
        
        return value
