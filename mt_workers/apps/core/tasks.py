import json
import random
import socket
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from celery import (task, current_app)
from celery.utils.log import get_task_logger
from elasticsearch import Elasticsearch
import websocket


log = get_task_logger('mt_workers.core')
es = Elasticsearch(settings.ELASTIC_HOST, sniff_on_start=True, sniff_on_connection_fail=True)
ws = websocket.WebSocket()
User = get_user_model()


@task(time_limit=30, default_retry_delay=10, max_retries=5, autoretry_for=(User.DoesNotExist,))
def test_task(total):
    """
    Task for celery/rabbitmq test.
    """
    log.info('<test_task> starts work.')

    for i in range(total):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        user = User.objects.create_user(username=username, email=email, password=password)
        ws.connect('ws://' + settings.SOCKETS_SERVER + '/chat/' + str(user.pk) + '/')
        ws.send(json.dumps({'text': random.randint(1, 1000)}))
        ws.close()
        queue = 'write_user_' + str(user.id)
        current_app.control.add_consumer(
            queue=queue, 
            exchange='elastic_write_user', 
            exchange_type='direct', 
            reply=True, 
            destination=['elastic_write_user@{}'.format(socket.gethostname())],
        )
        elastic_write_user.apply_async(['users', 'userprofile', user.id, {'username': username}], 
                                        queue=queue, routing_key=queue)
        User.objects.get(username=username, email=email).delete()
        result = '{} random users created with success!'.format(total)
    log.info('<test_task> {}.'.format(result))
    return result


@task(time_limit=1, default_retry_delay=1, max_retries=10, queue='elastic_read_user', autoretry_for=(Exception,))
def elastic_read_user(index, doc_type, _id):
    """
    Task for read from elasticsearch.
    """
    log.info('<elastic_read_user> starts work.')
    res = es.get(index=index, doc_type=doc_type, id=_id)
    log.info('<elastic_read_user> {}.'.format(res))
    return res


@task(time_limit=25, default_retry_delay=1, max_retries=5, autoretry_for=(Exception,))
def elastic_write_user(index, doc_type, _id, body):
    """
    Task for write in elasticsearch.
    """
    log.info('<elastic_write_user> starts work.')
    res = es.index(index=index, doc_type=doc_type, id=_id, body=body)
    result = None

    if res['created']:
        result = str(res['created']) + '. {} user successfully created in elastic search.'.format(_id)
        log.info('<elastic_write_user> {}.'.format(result))
    elif res['_version'] > 1:
        result = str(res['_version']) + '. {} user successfully updated in elastic search.'.format(_id)
        log.info('<elastic_write_user> {}.'.format(result))
    else:
        log.exception('<elastic_write_user> {} user was not recorded in elastic.'.format(_id))

    return result
