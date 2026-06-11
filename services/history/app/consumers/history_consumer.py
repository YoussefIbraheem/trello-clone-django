from logging import getLogger
from celery import Celery
from app.core.config import settings
from app.tasks.base_task import AsyncDBTask
from app.services.event_service import create_event
from kombu import Exchange, Queue

celery_app = Celery(
    "tasks", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND
)

logger = getLogger(__name__)
_dlx = Exchange("dlx", type="direct", durable=True)

celery_app.conf.update(
    task_ignore_result=True,
    task_routes=[
        {"app.consumers.history_consumer.record_activity": {"queue": "history"}}
    ],
    task_queues=[
        Queue(
            "history",
            Exchange("history", type="direct", durable=True),
            routing_key="history",
            queue_arguments={
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": "history.failed",
            },
        ),
        Queue("history.failed", _dlx, routing_key="history.failed", durable=True),
    ],
    task_default_exchange="history",
    task_default_routing_key="history",
)


@celery_app.task(
    base=AsyncDBTask,
    bind=True,
    name="app.consumers.history_consumer.record_activity",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    ignore_results=True,
)
def record_activity(self, event_data: dict):
    try:
        logger.info(f"Passed record:{event_data}")
        event_id = self.run_async(create_event(event_data))
        logger.info(f"Activity recorded successfully with ID: {event_id}")
    except Exception as e:
        logger.error(f"Failed to record activity: {e}", exc_info=True)
        raise
