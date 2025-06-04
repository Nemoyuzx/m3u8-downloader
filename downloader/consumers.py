import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from downloader.models import DownloadTask


class DownloadProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "download_progress"
        self.room_group_name = f"download_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'get_task_status':
            task_id = data.get('task_id')
            if task_id:
                task_data = await self.get_task_data(task_id)
                await self.send(text_data=json.dumps({
                    'type': 'task_status',
                    'task': task_data
                }))

    async def task_progress_update(self, event):
        """Send task progress update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'task_id': event['task_id'],
            'progress': event['progress'],
            'status': event['status'],
            'speed': event.get('speed'),
            'eta': event.get('eta'),
            'downloaded_segments': event.get('downloaded_segments'),
            'total_segments': event.get('total_segments')
        }))

    async def task_status_change(self, event):
        """Send task status change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'status_change',
            'task_id': event['task_id'],
            'status': event['status'],
            'message': event.get('message')
        }))

    @database_sync_to_async
    def get_task_data(self, task_id):
        """Get task data from database"""
        try:
            task = DownloadTask.objects.get(id=task_id)
            return {
                'id': str(task.id),
                'status': task.status,
                'progress': task.progress,
                'speed': task.speed,
                'eta': task.eta,
                'downloaded_segments': task.downloaded_segments,
                'total_segments': task.total_segments
            }
        except DownloadTask.DoesNotExist:
            return None
