from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import TaskHistory, SystemLog
from .serializers import (
    TaskHistorySerializer, 
    SystemLogSerializer,
    TaskHistoryFilterSerializer,
    SystemLogFilterSerializer
)


class TaskHistoryViewSet(viewsets.ModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        task_id = self.request.query_params.get('task_id')
        action = self.request.query_params.get('action')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        if action:
            queryset = queryset.filter(action=action)
        
        if start_date:
            try:
                start_dt = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__lte=end_dt)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent task history (last 24 hours)"""
        recent_time = timezone.now() - timedelta(hours=24)
        recent_history = self.queryset.filter(created_at__gte=recent_time)
        serializer = self.get_serializer(recent_history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_task(self, request):
        """Get history grouped by task"""
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task_history = self.queryset.filter(task_id=task_id)
        serializer = self.get_serializer(task_history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def cleanup_old(self, request):
        """Clean up old history records (older than 30 days)"""
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count, _ = self.queryset.filter(created_at__lt=cutoff_date).delete()
        
        return Response({
            'message': f'Cleaned up {deleted_count} old history records'
        })


class SystemLogViewSet(viewsets.ModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        level = self.request.query_params.get('level')
        module = self.request.query_params.get('module')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if level:
            queryset = queryset.filter(level=level.upper())
        
        if module:
            queryset = queryset.filter(module__icontains=module)
        
        if start_date:
            try:
                start_dt = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__lte=end_dt)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def errors(self, request):
        """Get error and critical logs"""
        error_logs = self.queryset.filter(level__in=['ERROR', 'CRITICAL'])
        serializer = self.get_serializer(error_logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent logs (last 24 hours)"""
        recent_time = timezone.now() - timedelta(hours=24)
        recent_logs = self.queryset.filter(created_at__gte=recent_time)
        serializer = self.get_serializer(recent_logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def cleanup_old(self, request):
        """Clean up old log records (older than 7 days)"""
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count, _ = self.queryset.filter(created_at__lt=cutoff_date).delete()
        
        return Response({
            'message': f'Cleaned up {deleted_count} old log records'
        })
