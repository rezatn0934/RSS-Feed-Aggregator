import json
import logging
from celery import shared_task, Task
from celery.worker.request import Request

from .utils import parse_podcast_data, create_or_update_categories, create_or_update_channel, create_items
from .models import XmlLink

logger = logging.getLogger('celery-logger')


class MyRequest(Request):
    'A minimal custom request to log failures and hard time limits.'

    def on_timeout(self, soft, timeout):
        super(MyRequest, self).on_timeout(soft, timeout)
        if not soft:
            logger.warning(
                f'A hard timeout was enforced for task task {self.task.name}'
            )

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super().on_failure(
            exc_info,
            send_failed_event=send_failed_event,
            return_ok=return_ok
        )
        logger.error(
            f'Failure detected for task {self.task.name}'
        )

    def on_success(self, failed__retval__runtime, **kwargs):
        logger.info(f"successful parse for task {self.task.name}")


class MyTask(Task):
    Request = MyRequest
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True


@shared_task(base=MyTask, bind=True, task_time_limit=60, acks_late=True)
def xml_link_creation(self, xml_link):
    xml_link = XmlLink.objects.get(xml_link=xml_link)

    [parsed_data, model] = parse_podcast_data(xml_link)
    channel_data = parsed_data['channel_data']['data']
    categories = create_or_update_categories(parsed_data['channel_data']['categories'])

    channel, status = create_or_update_channel(xml_link, channel_data)
    if status != 'exist':
        channel.category.set(categories)
        podcast_data = parsed_data['podcast_data']
        create_items(model, channel, podcast_data)

    return 'ok'

