import os

from django.conf import settings

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mt_workers.settings')

app = Celery('mt_workers')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
