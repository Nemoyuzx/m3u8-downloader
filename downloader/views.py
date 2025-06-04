from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DownloadTask
from .serializers import (
    DownloadTaskSerializer, 
    DownloadTaskCreateSerializer, 
    DownloadTaskUpdateSerializer
)
from .tasks import start_download_task


class DownloadTaskViewSet(viewsets.ModelViewSet):
    queryset = DownloadTask.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DownloadTaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DownloadTaskUpdateSerializer
        return DownloadTaskSerializer
    
    def create(self, request):
        """Create a new download task"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task = serializer.save()
        
        # Start the download task asynchronously
        start_download_task.delay(str(task.id))
        
        return Response(
            DownloadTaskSerializer(task).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a download task"""
        task = self.get_object()
        
        if task.status not in ['downloading']:
            return Response(
                {'error': 'Task is not in a pausable state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'paused'
        task.save()
        
        return Response({'message': 'Task paused successfully'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused download task"""
        task = self.get_object()
        
        if task.status not in ['paused', 'failed']:
            return Response(
                {'error': 'Task is not in a resumable state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'downloading'
        task.save()
        
        # Restart the download task
        start_download_task.delay(str(task.id))
        
        return Response({'message': 'Task resumed successfully'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a download task"""
        task = self.get_object()
        
        if task.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Task is already completed or cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'cancelled'
        task.save()
        
        return Response({'message': 'Task cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed download task"""
        task = self.get_object()
        
        if task.status not in ['failed']:
            return Response(
                {'error': 'Task is not in a retryable state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset task state
        task.status = 'pending'
        task.progress = 0.0
        task.downloaded_size = 0
        task.downloaded_segments = 0
        task.failed_segments = 0
        task.error_message = ''
        task.save()
        
        # Start the download task again
        start_download_task.delay(str(task.id))
        
        return Response({'message': 'Task retry started successfully'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active download tasks"""
        active_tasks = self.queryset.filter(
            status__in=['pending', 'downloading', 'merging']
        )
        serializer = self.get_serializer(active_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get all completed download tasks"""
        completed_tasks = self.queryset.filter(status='completed')
        serializer = self.get_serializer(completed_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get all failed download tasks"""
        failed_tasks = self.queryset.filter(status='failed')
        serializer = self.get_serializer(failed_tasks, many=True)
        return Response(serializer.data)
