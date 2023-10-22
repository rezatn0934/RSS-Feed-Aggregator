import json
import os
import pika
from django.conf import settings
from abc import ABC, abstractmethod
from interactions.models import Notification, Subscription, ActivityLog
from rssfeeds.models import Channel
from .models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


class EventConsumer(ABC):  # BaseEventConsumer
    """
    EventConsumer is an abstract base class defining the common structure for event consumers.
    Concrete event consumer classes will extend this and provide their own callback implementations.

    Attributes:
        event_type (str): The type of event this consumer handles.
        credentials (pika.PlainCredentials): Credentials for connecting to RabbitMQ.
        connection (pika.BlockingConnection): Connection to RabbitMQ.
        channel (pika.channel.Channel): Channel for communication with RabbitMQ.
    """

    def __init__(self, event_type):
        """
        Initializes an EventConsumer instance.

        Args:
            event_type (str): The type of event this consumer handles.
        """
        self.event_type = event_type
        self.credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        """
        Declares a queue in RabbitMQ.

        Args:
            queue_name (str): The name of the queue to declare.
        """
        print(f"Trying to declare queue({queue_name})...")
        self.channel.queue_declare(queue=queue_name)

    def consume_events(self, queue_name):
        """
        Begins consuming events from the specified queue.

        Args:
            queue_name (str): The name of the queue to consume events from.
        """
        self.declare_queue(queue_name=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback)
        self.channel.start_consuming()

    @abstractmethod
    def callback(self, ch, method, properties, body):
        """
        Callback method to be implemented by concrete event consumer classes.

        This method will be called when a new message is received in the queue.

        Args:
            ch: pika.channel.Channel
                The channel object through which the message was received.

            method: pika.spec.Basic.Deliver
                Delivery metadata such as delivery tag, redelivered flag, exchange, etc.

            properties: pika.spec.BasicProperties
                Properties of the message like content type, headers, etc.

            body: bytes
                The message body in bytes.
        """
        pass

    def close_connection(self):
        """
        Closes the connection to RabbitMQ.
        """
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

    @property
    def strategy(self) -> EventConsumer:
        """
        Gets the current event consumer strategy.

        Returns:
            EventConsumer: The current event consumer strategy.
        """
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: EventConsumer) -> None:
        """
        Sets a new event consumer strategy.

        Args:
            strategy (EventConsumer): The new event consumer strategy.
        """
        self._strategy = strategy

    def start_consuming(self, queue_name) -> None:
        """
        Starts consuming events using the selected strategy.

        Args:
            queue_name (str): The name of the queue to consume events from.
        """
        self._strategy.consume_events(queue_name=queue_name)


class UserEventConsumer(EventConsumer):
    """
    Event consumer for handling user-related events.
    """

    def callback(self, ch, method, properties, body):
        """
        Callback method to process user-related events received from RabbitMQ.

        Args:
            ch: pika.channel.Channel
                The channel object through which the message was received.

            method: pika.spec.Basic.Deliver
                Delivery metadata such as delivery tag, redelivered flag, exchange, etc.

            properties: pika.spec.BasicProperties
                Properties of the message like content type, headers, etc.

            body: bytes
                The message body in bytes.

        Note:
            This method will be called by RabbitMQ when a new message is received.
        """
        event_data = json.loads(body)
        data = event_data.get('data')
        user_id = data['user_id']
        user = User.objects.get(id=user_id)
        message = data['data']

        if self.event_type in ['login', 'register']:
            notification = Notification.objects.create(
                title=self.event_type,
                notification_type='info',
                message=message
            )
            notification.recipients.add(user)

            notification.save()
        ActivityLog.objects.update_or_create(user=user, action_type=self.event_type, remarks=message)

        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Received event: {self.event_type} for user: {user.username}")


class UpdateRSSConsumer(EventConsumer):
    """
    Event consumer for handling RSS update events.
    """

    def callback(self, ch, method, properties, body):
        """
        Callback method to process RSS update events received from RabbitMQ.

        Args:
            ch: pika.channel.Channel
                The channel object through which the message was received.

            method: pika.spec.Basic.Deliver
                Delivery metadata such as delivery tag, redelivered flag, exchange, etc.

            properties: pika.spec.BasicProperties
                Properties of the message like content type, headers, etc.

            body: bytes
                The message body in bytes.

        Note:
            This method will be called by RabbitMQ when a new message is received.
        """
        print(f"Received event: {self.event_type} for RSS update")
        event_data = json.loads(body)
        data = event_data.get('data')
        channel_id = data['channel_id']
        message = data['data']
        subscribers = Subscription.objects.filter(channel=Channel.objects.get(id=channel_id))

        if subscribers.exists():
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
