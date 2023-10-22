from django.utils.translation import gettext_lazy as _
import json
import logging

from core.parsers import PodcastParser, NewsParser
from core.models import Category
from .models import Podcast, News, Channel
import requests


def parse_data(xml_link):
    response = requests.get(xml_link.xml_link)
    [Parser, model] = item_model_mapper(xml_link.rss_type.name)
    return [Parser(response.text).parse_xml_and_create_records(), model]


def item_model_mapper(arg):
    choice = {
        "Podcast": [PodcastParser, Podcast],
        "News": [NewsParser, News],
    }
    return choice[arg.capitalize()]


def create_or_update_categories(categories_data):
    categories = []
    for category_data in categories_data:
        parent, _ = Category.objects.get_or_create(name=category_data.name)
        categories.append(parent)
        for child_data in category_data.children:
            child, _ = Category.objects.get_or_create(name=child_data.name, parent=parent)
            categories.append(child)
    return categories


def create_or_update_channel(xml_link, channel_data):
    status = 'created'
    channel, created = Channel.objects.get_or_create(xml_link=xml_link, defaults=channel_data)
    last_update = channel_data.get('last_update')
    if not created:
        if channel.last_update != last_update or not channel.last_update:
            for key, value in channel_data.items():
                setattr(channel, key, value)
            channel.save()
            status = 'updated'
        else:
            status = 'exist'
    return channel, status


def create_items(model, channel, podcast_data):
    podcast_items = (model(channel=channel, **item) for item in podcast_data if
                     not model.objects.filter(guid=item.get("guid")).exists())
    model.objects.bulk_create(podcast_items)


logger = logging.getLogger('elastic-logger')


def log_task_info(task_name, level, message, task_id, args, kwargs, retval=' ', exception=' ', retry_count=' ',
                  max_retries=' ', retry_eta=' '):

    log_data = {
        'event': f'CeleryTask.{task_name}',
        'level': level,
        'message': message,
        'task_id': task_id,
        'task_name': task_name,
        'input_data': {
            'args': args,
            'kwargs': kwargs
        },
        'output_data': retval,
        'exception': str(exception) if exception else None,
        'retry_count': retry_count,
        'max_retries': max_retries,
        'retry_eta': retry_eta
    }
    logger.log(getattr(logging, level.upper()), json.dumps(log_data))
