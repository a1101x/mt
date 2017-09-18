import json
import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import task
import websocket


@task(time_limit=30, default_retry_delay=10, max_retries=5)
def test_task(total):
    try:
        for i in range(total):
            username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
            email = '{}@example.com'.format(username)
            password = get_random_string(50)
            User.objects.create_user(username=username, email=email, password=password)
            user = User.objects.get(username=username, email=email)
            ws = websocket.WebSocket()
            ws.connect('ws://' + settings.SOCKETS_SERVER + '/chat/' + str(user.pk) + '/')
            ws.send(json.dumps({'text': random.randint(1, 1000)}))
            ws.close()
            User.objects.get(username=username, email=email).delete()
        return '{} random users created with success!'.format(total)
    except User.DoesNotExist:
        test_task.retry()
