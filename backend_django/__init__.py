"""Initialize Celery when Django starts."""

# This ensures the Celery app is loaded when Django
# starts so that the ``shared_task`` decorator uses
# our configured application. Without this import the
# tasks fall back to the default Celery app which uses
# ``pyamqp://guest@localhost//`` and results in connection
# errors if RabbitMQ is not running.
from .celery import app as celery_app

__all__ = ("celery_app",)
