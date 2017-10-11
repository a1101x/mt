from datetime import (datetime, timedelta)
import socket

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from celery import (task, current_app)
from celery.utils.log import get_task_logger
from kombu import (Connection, Exchange, Queue)
from twilio.rest import Client

from apps.userprofile.models import (RegistrationActivationEmail, RegistrationActivationSMS)
from apps.userprofile.utils import generate_code


log = get_task_logger('mt_workers.userprofile')
User = get_user_model()
conn = Connection(settings.CELERY_BROKER_URL)
channel = conn.channel()


@task(time_limit=10, default_retry_delay=2, max_retries=5, autoretry_for=(Exception,))
def send_sms(user_id, phone):
    """
    Create code for user activation and send sms using twilio.
    """
    log.info('<send_sms> starts work.')
    pin_code = generate_code()
    user = User.objects.get(id=user_id)
    time = datetime.now() + timedelta(minutes=15)
    RegistrationActivationSMS.objects.create(user=user, pin_code=pin_code, time_expired=time)
    context = {'code': pin_code}
    message = render_to_string('send_sms/send_email_activation_sms.txt', context=context)
    message = message.encode('utf-8')
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    response = client.messages.create(body=message, to=phone, from_=settings.TWILIO_NUMBER)
    log.info('<send_sms> {}.'.format(response))
    return response


@task(time_limit=10, default_retry_delay=2, max_retries=5, 
      autoretry_for=(User.DoesNotExist, RegistrationActivationEmail.DoesNotExist))
def send_login_email(user_id, email):
    """
    Create code for email login and send it via email.
    """
    log.info('<send_login_email> starts work.')
    activation_key = generate_code()
    user = User.objects.get(id=user_id)
    time = datetime.now() + timedelta(minutes=15)
    RegistrationActivationEmail.objects.create(user=user, activation_key=activation_key, time_expired=time)
    context = {'code': activation_key}
    user.set_password(activation_key)
    user.save()
    subject = render_to_string('send_mail/send_login_email_subject.txt')
    message = render_to_string('send_mail/send_login_email.txt', context=context)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    result = '<send_login_email> key {} for user {}.'.format(activation_key, email)
    log.info('<send_login_email> {}.'.format(result))
    return result


@task(time_limit=30, default_retry_delay=15, max_retries=5, autoretry_for=(RegistrationActivationEmail.DoesNotExist,))
def remove_sms_activation_keys():
    """
    Scheduled task. Removes old sms activation codes.
    """
    log.info('<remove_sms_activation_keys> starts work.')
    RegistrationActivationSMS.objects.filter(time_expired__lt=timezone.now()).delete()
    log.info('<remove_sms_activation_keys> done.')


@task(time_limit=300, default_retry_delay=5, max_retries=5, autoretry_for=(Exception,))
def cancel_write_user_consumers():
    """
    Scheduled task. Delete all consumers for user write.
    """
    log.info('<cancel_write_user_consumers> starts work.')
    worker = 'elastic_write_user@{}'.format(socket.gethostname())
    queues = current_app.control.inspect([worker]).active_queues()

    for queue in queues[worker]:
        if queue['name'].startswith('write_user_'):
            current_app.control.cancel_consumer(queue=queue['name'], destination=[worker], reply=True)
            exchange = Exchange(queue['name'], type='direct')
            bound_exchange = exchange(channel)
            bound_exchange.delete()
            _queue = Queue(queue['name'], exchange=exchange, routing_key=queue['name'])
            bound_queue = _queue(channel)
            bound_queue.delete()

    log.info('<cancel_write_user_consumers> done.')
