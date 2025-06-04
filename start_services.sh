#!/bin/bash

# 开始 Django 服务器
echo "启动 Django 后端服务器..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!
echo "Django 服务器已启动，PID: $DJANGO_PID"

# 启动 Celery worker
echo "启动 Celery worker..."
cd $(dirname $0)
celery -A backend_django worker -l info &
CELERY_PID=$!
echo "Celery worker 已启动，PID: $CELERY_PID"

echo "所有服务已启动"
echo "按 CTRL+C 停止所有服务"

# 捕获终止信号
trap "echo 正在停止所有服务...; kill $DJANGO_PID; kill $CELERY_PID; exit" SIGINT SIGTERM

# 保持脚本运行
wait
