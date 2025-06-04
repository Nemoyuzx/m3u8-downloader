from rest_framework import serializers
from .models import TaskHistory, SystemLog


class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = ['id', 'task_id', 'action', 'description', 'details', 'created_at']
        read_only_fields = ['id', 'created_at']


class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = ['id', 'level', 'message', 'module', 'function', 'line_number', 'extra_data', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskHistoryFilterSerializer(serializers.Serializer):
    task_id = serializers.UUIDField(required=False)
    action = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("start_date cannot be later than end_date")
        
        return data


class SystemLogFilterSerializer(serializers.Serializer):
    level = serializers.CharField(required=False)
    module = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("start_date cannot be later than end_date")
        
        return data
