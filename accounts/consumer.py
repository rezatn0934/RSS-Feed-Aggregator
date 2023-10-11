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
