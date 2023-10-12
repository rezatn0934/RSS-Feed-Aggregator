from celery import Task

from rssfeeds.utils import log_task_info


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
