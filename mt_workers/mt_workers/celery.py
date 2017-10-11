import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab
from kombu import (Queue, Exchange)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mt_workers.settings')

app = Celery('mt_workers')
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

app.conf.beat_schedule = {
    # Executes every day morning at 4:00 a.m.
    'remove_sms_activation_keys_at_4_am': {
        'task': 'apps.userprofile.tasks.remove_sms_activation_keys',
        'schedule': crontab(hour=4, minute=0),
    },
    # Executes every selected minute/hour. (from config)
    'cancel_write_user_consumers_schedule': {
        'task': 'apps.userprofile.tasks.cancel_write_user_consumers',
        'schedule': crontab(minute=settings.DELETE_CONSUMERS_MINUTE),
    },
}
