from django.core.management.base import BaseCommand
from accounts.consumer import UserEventConsumer, UpdateRSSConsumer
import threading


class Command(BaseCommand):
    help = 'Launches Consumer for login message: RabbitMQ'

    def handle(self, *args, **options):
        login_consumer = UserEventConsumer(event_type='login')
        register_consumer = UserEventConsumer(event_type='register')
        update_rss_consumer = UpdateRSSConsumer(event_type='update_rss')

        thread1 = threading.Thread(target=login_consumer.consume_events, kwargs={'queue_name': 'login'})
        thread2 = threading.Thread(target=register_consumer.consume_events, kwargs={'queue_name': 'register'})
        thread3 = threading.Thread(target=update_rss_consumer.consume_events, kwargs={'queue_name': 'update_rss'})

        thread1.start()
        thread2.start()
        thread3.start()
