from celery import shared_task
from django.utils import timezone
from .models import DownloadTask, DownloadSegment
from .utils.m3u8_parser import M3U8Parser
from .utils.downloader import SegmentDownloader
from files.models import DownloadedFile
from tasks.models import TaskHistory
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


@shared_task
def start_download_task(task_id):
    """Start downloading a m3u8 task"""
    try:
        task = DownloadTask.objects.get(id=task_id)
        
        if task.status != 'pending':
            logger.info(f"Task {task_id} is not in pending state, skipping")
            return
        
        # Update task status
        task.status = 'downloading'
        task.started_at = timezone.now()
        task.save()
        
        # Log task start
        TaskHistory.objects.create(
            task_id=task.id,
            action='download_started',
            description=f'Started downloading: {task.title or task.url}'
        )
        
        # Parse M3U8 file
        parser = M3U8Parser()
        segments, encryption_info = parser.parse(task.url, task.headers)
        
        if not segments:
            task.status = 'failed'
            task.error_message = 'Failed to parse M3U8 file or no segments found'
            task.save()
            return
        
        # Update task with segment info
        task.total_segments = len(segments)
        task.encryption_key = encryption_info.get('key', '')
        task.encryption_iv = encryption_info.get('iv', '')
        task.save()
        
        # Create temp directory
        temp_dir = os.path.join(tempfile.gettempdir(), f'download_{task_id}')
        os.makedirs(temp_dir, exist_ok=True)
        task.temp_dir = temp_dir
        task.save()
        
        # Create segment records
        for i, segment_url in enumerate(segments):
            DownloadSegment.objects.create(
                task=task,
                index=i,
                url=segment_url
            )
        
        # Start downloading segments
        download_segments.delay(task_id)
        
    except DownloadTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
    except Exception as e:
        logger.error(f"Error starting download task {task_id}: {str(e)}")
        try:
            task = DownloadTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
        except:
            pass


@shared_task
def download_segments(task_id):
    """Download all segments for a task"""
    try:
        task = DownloadTask.objects.get(id=task_id)
        
        if task.status != 'downloading':
            logger.info(f"Task {task_id} is not in downloading state, skipping")
            return
        
        downloader = SegmentDownloader()
        segments = task.segments.filter(status='pending').order_by('index')
        
        for segment in segments:
            if task.status != 'downloading':
                logger.info(f"Task {task_id} status changed, stopping download")
                break
            
            # Download individual segment
            download_single_segment.delay(task_id, segment.id)
        
        # Check if all segments are downloaded
        check_download_completion.delay(task_id)
        
    except Exception as e:
        logger.error(f"Error downloading segments for task {task_id}: {str(e)}")


@shared_task
def download_single_segment(task_id, segment_id):
    """Download a single segment"""
    try:
        task = DownloadTask.objects.get(id=task_id)
        segment = DownloadSegment.objects.get(id=segment_id)
        
        if task.status != 'downloading':
            return
        
        segment.status = 'downloading'
        segment.save()
        
        downloader = SegmentDownloader()
        file_path = downloader.download_segment(
            segment.url,
            task.temp_dir,
            segment.index,
            headers=task.headers,
            encryption_key=task.encryption_key,
            encryption_iv=task.encryption_iv
        )
        
        if file_path:
            segment.status = 'completed'
            segment.file_path = file_path
            segment.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            segment.completed_at = timezone.now()
            segment.save()
            
            # Update task progress
            completed_segments = task.segments.filter(status='completed').count()
            task.downloaded_segments = completed_segments
            task.progress = (completed_segments / task.total_segments) * 100
            task.save()
            
        else:
            segment.status = 'failed'
            segment.retry_count += 1
            segment.save()
            
            task.failed_segments += 1
            task.save()
            
            # Retry if under limit
            if segment.retry_count < 3:
                download_single_segment.delay(task_id, segment_id)
        
    except Exception as e:
        logger.error(f"Error downloading segment {segment_id}: {str(e)}")


@shared_task
def check_download_completion(task_id):
    """Check if download is complete and start merging"""
    try:
        task = DownloadTask.objects.get(id=task_id)
        
        completed_segments = task.segments.filter(status='completed').count()
        total_segments = task.total_segments
        
        if completed_segments == total_segments:
            # All segments downloaded, start merging
            task.status = 'merging'
            task.save()
            
            TaskHistory.objects.create(
                task_id=task.id,
                action='merge_started',
                description='Starting to merge segments'
            )
            
            merge_segments.delay(task_id)
            
        elif task.failed_segments > 0 and (completed_segments + task.failed_segments) == total_segments:
            # Some segments failed permanently
            task.status = 'failed'
            task.error_message = f'Failed to download {task.failed_segments} segments'
            task.save()
            
            TaskHistory.objects.create(
                task_id=task.id,
                action='download_failed',
                description=f'Download failed: {task.failed_segments} segments could not be downloaded'
            )
        
    except Exception as e:
        logger.error(f"Error checking completion for task {task_id}: {str(e)}")


@shared_task
def merge_segments(task_id):
    """Merge downloaded segments into final video file"""
    try:
        task = DownloadTask.objects.get(id=task_id)
        
        if task.status != 'merging':
            return
        
        from .utils.merger import VideoMerger
        merger = VideoMerger()
        
        # Get all segment files in order
        segments = task.segments.filter(status='completed').order_by('index')
        segment_files = [seg.file_path for seg in segments if os.path.exists(seg.file_path)]
        
        if not segment_files:
            task.status = 'failed'
            task.error_message = 'No segment files found for merging'
            task.save()
            return
        
        # Determine output filename
        output_filename = task.title or f'download_{task.id}'
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = task.output_path or os.path.join(
            os.path.expanduser('~/Downloads'),
            output_filename
        )
        
        # Merge segments
        success = merger.merge_segments(segment_files, output_path)
        
        if success:
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.output_path = output_path
            task.save()
            
            # Create file record
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            DownloadedFile.objects.create(
                filename=os.path.basename(output_path),
                original_name=task.title or '',
                file_path=output_path,
                file_size=file_size,
                file_type='video',
                download_task_id=task.id
            )
            
            # Log completion
            TaskHistory.objects.create(
                task_id=task.id,
                action='download_completed',
                description=f'Download completed: {output_filename}'
            )
            
            # Clean up temp files
            cleanup_temp_files.delay(task_id)
            
        else:
            task.status = 'failed'
            task.error_message = 'Failed to merge segments'
            task.save()
            
            TaskHistory.objects.create(
                task_id=task.id,
                action='merge_failed',
                description='Failed to merge segments into final video'
            )
        
    except Exception as e:
        logger.error(f"Error merging segments for task {task_id}: {str(e)}")
        try:
            task = DownloadTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
        except:
            pass


@shared_task
def cleanup_temp_files(task_id):
    """Clean up temporary files after successful download"""
    try:
        task = DownloadTask.objects.get(id=task_id)
        
        if task.temp_dir and os.path.exists(task.temp_dir):
            import shutil
            shutil.rmtree(task.temp_dir)
            logger.info(f"Cleaned up temp directory for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error cleaning up temp files for task {task_id}: {str(e)}")
