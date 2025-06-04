from rest_framework import serializers
from .models import DownloadedFile
import os


class DownloadedFileSerializer(serializers.ModelSerializer):
    file_exists = serializers.SerializerMethodField()
    
    class Meta:
        model = DownloadedFile
        fields = [
            'id', 'filename', 'original_name', 'file_path', 'file_size', 
            'file_size_formatted', 'file_type', 'mime_type', 'duration', 
            'resolution', 'format', 'download_task_id', 'created_at', 
            'modified_at', 'file_exists'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at', 'file_size_formatted']
    
    def get_file_exists(self, obj):
        return os.path.exists(obj.file_path)


class FileActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['delete', 'move', 'rename'])
    target_path = serializers.CharField(required=False, allow_blank=True)
    new_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        action = data.get('action')
        
        if action == 'move' and not data.get('target_path'):
            raise serializers.ValidationError("target_path is required for move action")
        
        if action == 'rename' and not data.get('new_name'):
            raise serializers.ValidationError("new_name is required for rename action")
        
        return data


class BulkFileActionSerializer(serializers.Serializer):
    file_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['delete', 'move'])
    target_path = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        action = data.get('action')
        
        if action == 'move' and not data.get('target_path'):
            raise serializers.ValidationError("target_path is required for move action")
        
        return data
