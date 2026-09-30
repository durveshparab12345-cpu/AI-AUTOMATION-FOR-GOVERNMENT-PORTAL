"""
Celery application configuration.

This module configures Celery for asynchronous task processing,
defining task queue, broker, and result backend configuration.
"""

from celery import Celery
from celery.schedules import crontab

# TODO: Import from config
# from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "ai_portal",
    broker="redis://localhost:6379/0",  # TODO: Use config
    backend="redis://localhost:6379/1",  # TODO: Use config
)

# TODO: Load configuration from settings
# celery_app.conf.update(
#     broker_url=settings.redis_url,
#     result_backend=settings.redis_backend_url,
#     accept_content=['json'],
#     task_serializer='json',
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
# )

# Task routing
celery_app.conf.task_routes = {
    'app.workers.tasks.automation_tasks.*': {'queue': 'automation'},
    'app.workers.tasks.document_tasks.*': {'queue': 'documents'},
    'app.workers.tasks.notification_tasks.*': {'queue': 'notifications'},
    'app.workers.tasks.scheduling_tasks.*': {'queue': 'scheduler'},
}

# Task configuration
celery_app.conf.task_default_queue = 'default'
celery_app.conf.task_default_exchange = 'tasks'
celery_app.conf.task_default_routing_key = 'task.default'

# Result backend configuration
celery_app.conf.result_expires = 3600  # Results expire after 1 hour

# Task time limits
celery_app.conf.task_time_limit = 30 * 60  # Hard limit: 30 minutes
celery_app.conf.task_soft_time_limit = 25 * 60  # Soft limit: 25 minutes

# Retry configuration
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_max_retries = 3

# Periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    'check-workflow-timeouts': {
        'task': 'app.workers.tasks.scheduling_tasks.check_execution_timeouts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-audit-logs': {
        'task': 'app.workers.tasks.scheduling_tasks.cleanup_old_audit_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'sync-portal-status': {
        'task': 'app.workers.tasks.automation_tasks.sync_portal_status',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    # TODO: Add more periodic tasks
}


@celery_app.task(bind=True)
def debug_task(self):
    """
    Debug task for testing Celery setup.

    Args:
        self: Task instance

    Returns:
        Debug message
    """
    return f'Request: {self.request!r}'


def get_celery_app():
    """
    Get the Celery app instance.

    Returns:
        Configured Celery app
    """
    return celery_app
