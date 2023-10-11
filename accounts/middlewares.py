from accounts.utils import log_entry
import json
import logging

logger = logging.getLogger('elastic-logger')


class LoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
