import os

from django.conf import settings

from celery import Celery
from kombu import (Queue, Exchange)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mt_server.settings')

app = Celery('mt_server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_default_queue = 'default'
app.conf.task_queues = (
    Queue('default', Exchange('default', type='direct'), routing_key='default', 
          consumer_arguments={'x-max-priority': 0}),
    Queue('elastic_write_user', Exchange('elastic_write_user', type='direct'), routing_key='elastic_write_user', 
          consumer_arguments={'x-max-priority': 10}),
    Queue('elastic_read_user', Exchange('elastic_read_user', type='direct'), routing_key='elastic_read_user', 
          consumer_arguments={'x-max-priority': 3}),
)
task_default_exchange = 'default'
task_default_exchange_type = 'direct'
task_default_routing_key = 'default'
app.autodiscover_tasks()
