from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import DownloadedFile
from .serializers import DownloadedFileSerializer, FileActionSerializer, BulkFileActionSerializer
import os
import shutil
import logging

logger = logging.getLogger(__name__)


class DownloadedFileViewSet(viewsets.ModelViewSet):
    queryset = DownloadedFile.objects.all()
    serializer_class = DownloadedFileSerializer
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download a file"""
        file_obj = self.get_object()
        
        if not os.path.exists(file_obj.file_path):
            return Response(
                {'error': 'File not found on disk'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            response = FileResponse(
                open(file_obj.file_path, 'rb'),
                as_attachment=True,
                filename=file_obj.filename
            )
            return response
        except Exception as e:
            logger.error(f"Error serving file {file_obj.file_path}: {str(e)}")
            return Response(
                {'error': 'Error serving file'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def file_action(self, request, pk=None):
        """Perform action on a file (delete, move, rename)"""
        file_obj = self.get_object()
        serializer = FileActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        
        try:
            if action_type == 'delete':
                return self._delete_file(file_obj)
            elif action_type == 'move':
                target_path = serializer.validated_data['target_path']
                return self._move_file(file_obj, target_path)
            elif action_type == 'rename':
                new_name = serializer.validated_data['new_name']
                return self._rename_file(file_obj, new_name)
            
        except Exception as e:
            logger.error(f"Error performing {action_type} on file {file_obj.id}: {str(e)}")
            return Response(
                {'error': f'Error performing {action_type}: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk action on multiple files"""
        serializer = BulkFileActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file_ids = serializer.validated_data['file_ids']
        action_type = serializer.validated_data['action']
        
        files = DownloadedFile.objects.filter(id__in=file_ids)
        results = {'success': [], 'failed': []}
        
        for file_obj in files:
            try:
                if action_type == 'delete':
                    result = self._delete_file(file_obj)
                elif action_type == 'move':
                    target_path = serializer.validated_data['target_path']
                    result = self._move_file(file_obj, target_path)
                
                if result.status_code == 200:
                    results['success'].append(file_obj.id)
                else:
                    results['failed'].append({
                        'id': file_obj.id,
                        'error': result.data.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'id': file_obj.id,
                    'error': str(e)
                })
        
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get file statistics"""
        total_files = self.queryset.count()
        total_size = sum(f.file_size for f in self.queryset.all())
        
        by_type = {}
        for file_obj in self.queryset.all():
            file_type = file_obj.file_type
            if file_type not in by_type:
                by_type[file_type] = {'count': 0, 'size': 0}
            by_type[file_type]['count'] += 1
            by_type[file_type]['size'] += file_obj.file_size
        
        return Response({
            'total_files': total_files,
            'total_size': total_size,
            'total_size_formatted': self._format_size(total_size),
            'by_type': by_type
        })
    
    def _delete_file(self, file_obj):
        """Delete a file"""
        try:
            # Delete from disk
            if os.path.exists(file_obj.file_path):
                os.remove(file_obj.file_path)
            
            # Delete from database
            file_obj.delete()
            
            return Response({'message': 'File deleted successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Error deleting file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _move_file(self, file_obj, target_path):
        """Move a file to a new location"""
        try:
            # Ensure target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Move file
            shutil.move(file_obj.file_path, target_path)
            
            # Update database record
            file_obj.file_path = target_path
            file_obj.filename = os.path.basename(target_path)
            file_obj.save()
            
            return Response({'message': 'File moved successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Error moving file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _rename_file(self, file_obj, new_name):
        """Rename a file"""
        try:
            old_path = file_obj.file_path
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            # Rename file
            os.rename(old_path, new_path)
            
            # Update database record
            file_obj.file_path = new_path
            file_obj.filename = new_name
            file_obj.save()
            
            return Response({'message': 'File renamed successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Error renaming file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _format_size(self, size):
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.1f} MB"
        else:
            return f"{size / (1024 ** 3):.1f} GB"
