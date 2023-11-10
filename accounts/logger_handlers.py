import json
import logging
import time
from datetime import datetime
from django.conf import settings
from elasticsearch import Elasticsearch


class ElasticHandler(logging.Handler):
    """
    Custom logging handler for sending log records to Elasticsearch.

    This handler sends log records to Elasticsearch with a specified index name and timestamp.

    Attributes:
        es (Elasticsearch): Elasticsearch client instance for log storage.
        sender (LogSender): Log sender instance for writing log records.

    Methods:
        emit(self, record):
            Emit a log record to Elasticsearch.

    Example Usage:
        To use this custom logging handler, add it to your Django logging configuration.
        It sends log records to Elasticsearch with the specified index name and timestamp.

    Note:
        - If there is an exception during log emission, it is handled, and the error is logged.
        - The Elasticsearch host and port are configured from Django settings.

    See the Elasticsearch Python client documentation for more details on usage.
    """

    def __init__(self):
        super().__init__()
        self.es = Elasticsearch(f'http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}')
        self.sender = LogSender(self.es)

    def emit(self, record):
        try:
            self.sender.writeLog(record, formatter=self.format)
        except Exception:
            self.handleError(record)


class LogSender:
    """
    Log sender for writing log records to Elasticsearch.

    Attributes:
        es (Elasticsearch): Elasticsearch client instance for log storage.

    Methods:
        writeLog(self, msg: logging.LogRecord, formatter):
            Write a log record to Elasticsearch with a timestamp.

    Args:
        msg (logging.LogRecord): The log record to be written to Elasticsearch.
        formatter (function): The log record formatter function.

    Returns:
        None

    Example Usage:
        This class is used by the `ElasticHandler` to format and send log records to Elasticsearch.

    Note:
        - Log records are sent to Elasticsearch with a timestamp and specified index name.
        - The Elasticsearch client instance is provided during initialization.

    See the Elasticsearch Python client documentation for more details on usage.
    """

    def __init__(self, es):
        self.es = es

    def writeLog(self, msg: logging.LogRecord, formatter):
        index_name = f'log_{time.strftime("%Y_%m_%d")}'
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        log_data = json.loads(formatter(msg))
        log_data['timestamp'] = timestamp
        log_data['level'] = msg.levelname.lower()
        self.es.index(index=index_name, document=log_data)
