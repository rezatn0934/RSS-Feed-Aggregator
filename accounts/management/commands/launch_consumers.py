from django.core.management.base import BaseCommand
from accounts.consumer import UserEventConsumer, UpdateRSSConsumer, Context
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

        # Create instances of event consumers for different event types
        login_consumer = UserEventConsumer(event_type='login')
        register_consumer = UserEventConsumer(event_type='register')
        update_rss_consumer = UpdateRSSConsumer(event_type='update_rss')

        # Create contexts for each consumer
        context1 = Context(login_consumer)
        context2 = Context(register_consumer)
        context3 = Context(update_rss_consumer)

        # Start separate threads to consume events for each type
        thread1 = threading.Thread(target=context1.start_consuming, kwargs={'queue_name': 'login'})
        thread2 = threading.Thread(target=context2.start_consuming, kwargs={'queue_name': 'register'})
        thread3 = threading.Thread(target=context3.start_consuming, kwargs={'queue_name': 'update_rss'})

        # Start the threads
        thread1.start()
        thread2.start()
        thread3.start()
