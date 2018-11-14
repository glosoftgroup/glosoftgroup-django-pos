import logging
from django.conf import settings


class CustomFilter(logging.Filter):
    def __init__(self):
        self.environment = settings.ENV_NAME
        super(CustomFilter, self).__init__()

    def filter(self, record):
        record.environment = self.environment
        return True


__version__ = 'dev'

