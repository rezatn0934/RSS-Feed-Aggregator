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

