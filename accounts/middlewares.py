import uuid

from accounts.utils import log_entry
import json
import logging

logger = logging.getLogger('elastic-logger')


class LoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)
        log_data = log_entry(request, response)
        logger.info(json.dumps(log_data))
        return response

    def process_exception(self, request, exception):
        log_data = log_entry(request, None, exception)
        logger.error(json.dumps(log_data))
