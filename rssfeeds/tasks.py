from django.utils.translation import gettext_lazy as _
from celery import shared_task

from accounts.publishers import EventPublisher
from core.base_task import MyTask
from .utils import parse_data, create_or_update_categories, create_or_update_channel, create_items, log_task_info
from .models import XmlLink, Channel


@shared_task(base=MyTask, bind=True, task_time_limit=60, acks_late=True)
def xml_link_creation(self, xml_link, correlation_id):
    xml_link = XmlLink.objects.get(xml_link=xml_link)

    [parsed_data, model] = parse_data(xml_link)
    channel_data = parsed_data['channel_data']['data']
    categories = create_or_update_categories(parsed_data['channel_data']['categories'])

    channel, status = create_or_update_channel(xml_link, channel_data)
    if status != 'exist':
        channel.category.set(categories)
        channel.save()
        podcast_data = parsed_data['podcast_data']
        create_items(model, channel, podcast_data)

        data = {
            'channel_id': channel.id,
            'data': f'{channel.title} has been updated'
        }
        publisher = EventPublisher()
        publisher.publish_event('update_rss', 'update_rss', data=data)
        publisher.close_connection()

    return {
        'status': status,
        'message': f'Task {self.name} completed successfully for XML link: {xml_link}'
    }


@shared_task(base=MyTask, bind=True, soft_time_limit=900, task_time_limit=1000, acks_late=True)
def update_rssfeeds(self, correlation_id):
    xml_links = XmlLink.objects.all()
    for xml_link in xml_links:
        if Channel.objects.filter(xml_link=xml_link).exists():
            xml_link_creation.delay(xml_link.xml_link, correlation_id)
        else:
            xml_link.delete()  # add is_deleted to model
            log_task_info(
                task_name='update_rssfeeds', level='info',
                message=f'XML link deleted due to no related channel: {xml_link.xml_link}',
                task_id=self.request.id, args=[xml_link.xml_link], retval='XML link deleted', kwargs={}
            )

    return {
        'status': 'success',
        'message': f'Task {self.name} completed successfully for {len(xml_links)} XML links'
    }
