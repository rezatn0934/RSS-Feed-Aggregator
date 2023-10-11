import json
import logging
import time
from datetime import datetime
from django.conf import settings
from elasticsearch import Elasticsearch


class ElasticHandler(logging.Handler):

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
    def __init__(self, es):
        self.es = es

    def writeLog(self, msg: logging.LogRecord, formatter):
        index_name = f'log_{time.strftime("%Y_%m_%d")}'
        timestamp = datetime.utcnow().strftime('%d/%b/%Y:%H:%M:%S +0000')
        log_data = json.loads(formatter(msg))
        log_data['timestamp'] = timestamp

        self.es.index(index=index_name, document=log_data)
