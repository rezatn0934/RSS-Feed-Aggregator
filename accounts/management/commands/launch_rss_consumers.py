from django.core.management.base import BaseCommand
from accounts.consumers import UpdateRSSConsumer, Context
import threading


class Command(BaseCommand):
    """
    Custom management command to launch consumers for handling various types of events.

    This command starts multiple threads to consume events for different types.

    Usage:
        python manage.py launch_consumers
    """

    help = 'Launches Consumers for handling login, register, and update_rss events using RabbitMQ.'

    def handle(self, *args, **options):
        """
        Handles the execution of the management command.

        Args:
            args: Additional command-line arguments.
            options: Additional command-line options.
        """
        consumer = UpdateRSSConsumer(event_type='update_rss')
        context = Context(consumer)
        threads = threading.Thread(target=context.start_consuming, kwargs={'queue_name': 'update_rss'})
        threads.start()
