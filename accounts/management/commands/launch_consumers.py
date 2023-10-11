from django.core.management.base import BaseCommand
from accounts.consumer import UserEventConsumer, UpdateRSSConsumer
import threading


class Command(BaseCommand):
    help = 'Launches Consumer for login message : RabbitMQ'

