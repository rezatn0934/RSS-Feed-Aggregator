from accounts.utils import log_entry
import json
import logging

logger = logging.getLogger('elastic-logger')


class LoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.exception_occurred = False

    def __call__(self, request):
        self.exception_occurred = False

        response = self.get_response(request)
        log_data = log_entry(request, response)
        if not self.exception_occurred:
            logger.info(json.dumps(log_data))
        return response

    def process_exception(self, request, exception):
        self.exception_occurred = True
        log_data = log_entry(request, None, exception)
        logger.error(json.dumps(log_data))
