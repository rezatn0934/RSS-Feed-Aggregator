from django.core.management.base import BaseCommand
from accounts.consumers import UserEventConsumer, UpdateRSSConsumer, Context
import threading


class Command(BaseCommand):
    """
    Custom management command to launch consumers for handling various types of events.

    This command starts multiple threads to consume events for different types.

    Usage:
        python manage.py launch_consumers
    """

    help = 'Launches Consumers for login, register, and update_rss messages using RabbitMQ.'

    def handle(self, *args, **options):
        """
        Handles the execution of the management command.

        Args:
            args: Additional command-line arguments.
            options: Additional command-line options.
        """

        event_types = ['login', 'register', 'logout', 'change_pass', 'forget_pass', 'reset_password', 'update_rss']
        queue_names = ['login', 'register', 'logout', 'change_pass', 'forget_pass', 'reset_password', 'update_rss']

        consumers = [UserEventConsumer(event_type=event_type) for event_type in event_types]

        contexts = [Context(consumer) for consumer in consumers]

        threads = [threading.Thread(target=context.start_consuming, kwargs={'queue_name': queue_name})
                   for context, queue_name in zip(contexts, queue_names)]

        for thread in threads:
            thread.start()
