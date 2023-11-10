from celery import shared_task

from accounts.utils import custom_sen_mail
from core.base_task import MyTask


@shared_task(base=MyTask, bind=True, task_time_limit=60, acks_late=True)
def send_email_task(self, reset_link, email, correlation_id):
    custom_sen_mail('reset password', f"Your password rest link: {reset_link}", email)

    return {
        'status': 'success',
        'message': f'Password reset email sent to {email}',
    }
