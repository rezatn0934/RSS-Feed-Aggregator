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
        log_to_elasticsearch(log_data, log_level='info')
        return response
