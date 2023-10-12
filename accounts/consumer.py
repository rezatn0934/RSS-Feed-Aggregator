import json
import os
import pika
from abc import ABC, abstractmethod
from interactions.models import Notification, Subscription
from rssfeeds.models import Channel
from .models import User

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


class EventConsumer(ABC):
    def __init__(self, event_type):
        self.event_type = event_type
        self.credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        print(f"Trying to declare queue({queue_name})...")
        self.channel.queue_declare(queue=queue_name)

    def consume_events(self, queue_name):
        self.declare_queue(queue_name=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    @abstractmethod
    def callback(self, ch, method, properties, body):
        pass

    def close_connection(self):
        self.connection.close()


class Context:
    """
    The Context defines the interface of interest to clients.
    """

    def __init__(self, strategy: EventConsumer) -> None:
        """
        Initializes a Context instance with a specific event consumer strategy.

        Args:
            strategy (EventConsumer): The event consumer strategy to be used.
        """
        self._strategy = strategy


class UserEventConsumer(EventConsumer):
    def callback(self, ch, method, properties, body):
        event_data = json.loads(body)
        data = event_data.get('data')
        user_id = data['user_id']
        message = data['data']
        notification = Notification.objects.create(
            title=self.event_type,
            notification_type='info',
            message=message
        )
        user = User.objects.get(id=user_id)
        notification.recipients.add(user)

        notification.save()
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Received event: {self.event_type} for user: {user.username}")


class UpdateRSSConsumer(EventConsumer):
    def callback(self, ch, method, properties, body):
        print(f"Received event: {self.event_type} for RSS update")
        event_data = json.loads(body)
        data = event_data.get('data')
        channel_id = data['channel_id']
        message = data['data']
        subscribers = Subscription.objects.filter(channel=Channel.objects.get(id=channel_id))

        notification = Notification.objects.create(
            title=self.event_type,
            notification_type='info',
            message=message
        )

        for subscriber in subscribers:
            user = User.objects.get(id=subscriber.user_id)
            notification.recipients.add(user)

        notification.save()
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

