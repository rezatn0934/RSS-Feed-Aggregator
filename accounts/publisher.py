from django.conf import settings
import json
import os
import pika


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


class EventPublisher:
    def __init__(self):
        self.credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        print(f"Trying to declare queue({queue_name})...")
        self.channel.queue_declare(queue=queue_name)

    def publish_event(self, queue_name, event_type, data, exchange=''):
        event_data = {
            'event_type': event_type,
            'data': data
        }

        message = json.dumps(event_data)
        self.declare_queue(queue_name=queue_name)
        self.channel.basic_publish(exchange=exchange, routing_key=queue_name, body=message)
        print(f"Sent message. Exchange: {exchange}, Routing Key: {queue_name}")

