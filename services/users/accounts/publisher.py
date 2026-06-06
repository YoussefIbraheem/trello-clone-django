from celery import shared_task
from users import celery_app
from kombu import Producer, Exchange, Connection
import logging
import uuid

logger = logging.getLogger(__name__)


@shared_task
def publish_history_event(event_data):
    try:
        logger.info(f"Publishing history event: {event_data}")
        with Connection(celery_app.conf.broker_url) as conn:
            with conn.channel() as channel:
                producer = Producer(
                    channel,
                    exchange=Exchange("history", type="direct", durable=True),
                    routing_key="history",
                )
                producer.publish(
                    body={
                        "task": "app.consumers.history_consumer.record_activity",
                        "id": str(uuid.uuid4()),
                        "args": [event_data],
                        "kwargs": {},
                        "retries": 0,
                    },
                    declare=[],
                    serializer="json",
                )
        logger.info("History event published successfully.")
    except Exception as e:
        logger.error(f"Error publishing history event: {e}", exc_info=True)
        raise