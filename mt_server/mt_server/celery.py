import os

from django.conf import settings

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mt_server.settings')

app = Celery('mt_server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
