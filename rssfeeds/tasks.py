from celery import shared_task, Task
from accounts.publisher import EventPublisher
from .utils import parse_data, create_or_update_categories, create_or_update_channel, create_items, log_task_info
from .models import XmlLink, Channel


class MyTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True

    def retry(self, args=None, kwargs=None, exc=None, throw=True,
              eta=None, countdown=None, max_retries=None, **options):
        retry_count = self.request.retries
        retry_eta = eta or (countdown and f'countdown={countdown}') or 'default'
        log_task_info(self.name, 'warning', f'Retrying task {self.name} (retry {retry_count}) in {retry_eta} seconds',
                      self.request.id, args, kwargs, exception=exc, retry_count=retry_count, max_retries=max_retries,
                      retry_eta=retry_eta)

        super().retry(args, kwargs, exc, throw, eta, countdown, max_retries, **options)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        log_task_info(self.name, 'error', f'Task {self.name} failed: {str(exc)}',
                      task_id, args, kwargs, exception=exc)

    def on_success(self, retval, task_id, args, kwargs):
        log_task_info(self.name, 'info', f'Task {self.name} completed successfully', task_id, args, kwargs, retval)


@shared_task(base=MyTask, bind=True, task_time_limit=60, acks_late=True)
def xml_link_creation(self, xml_link):
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
        publisher.publish_event('update_rssfeed', 'update_rss', data=data)
        publisher.close_connection()

    return {
        'status': 'ok',
        'message': f'Task {self.name} completed successfully for XML link: {xml_link}'
    }


@shared_task(base=MyTask, bind=True, soft_time_limit=900, task_time_limit=1000, acks_late=True)
def update_rssfeeds(self):
    xml_links = XmlLink.objects.all()
    for xml_link in xml_links:
        if Channel.objects.filter(xml_link=xml_link).exists():
            xml_link_creation.delay(xml_link.xml_link)
        else:
            xml_link.delete()
            log_task_info(
                task_name='update_rssfeeds', level='info',
                message=f'XML link deleted due to no related channel: {xml_link.xml_link}',
                task_id=self.request.id, args=[xml_link.xml_link], retval='XML link deleted', kwargs={}
            )

    return {
        'status': 'ok',
        'message': f'Task {self.name} completed successfully for {len(xml_links)} XML links'
    }
