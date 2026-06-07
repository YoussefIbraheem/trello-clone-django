import json
import uuid

import pika
from app import logger, settings


def publish_history_event(event_data):

    with pika.BlockingConnection(pika.URLParameters(settings.BROKER_URL)) as connection:
        channel = connection.channel()
        channel.queue_declare(
            queue="history",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": "history.failed",
                "type": "direct",
            },
        )
        message_body = json.dumps(
            {
                "task": "app.consumers.history_consumer.record_activity",
                "id": str(uuid.uuid4()),
                "args": [event_data],
                "kwargs": {},
                "retries": 0,
            }
        )

        channel.basic_publish(
            exchange="history",
            routing_key="history",
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info(" [x] Sent event history %r" % event_data)

        connection.close()

    return
