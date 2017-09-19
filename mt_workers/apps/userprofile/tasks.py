from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from twilio.rest import Client
from celery import task

from apps.userprofile.models import RegistrationActivationEmail, RegistrationActivationSMS
from apps.userprofile.utils import generate_code, generate_pin_code


User = get_user_model()


@task(time_limit=30, default_retry_delay=2, max_retries=5)
def send_sms(user_id, phone):
    try:
        pin_code = generate_pin_code()
        user = User.objects.get(id=user_id)
        RegistrationActivationSMS.objects.create(user=user, pin_code=pin_code)
        context = {
            'code': pin_code,
        }

        message = render_to_string('send_sms/send_email_activation_sms.txt', context=context)
        message = message.encode('utf-8')
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        response = client.messages.create(body=message, to=phone, from_=settings.TWILIO_NUMBER)
        return response
    except User.DoesNotExist:
        send_sms.retry()


@task(time_limit=30, default_retry_delay=2, max_retries=5)
def send_activation_email(user_id, email):
    activation_key = generate_code()
    user = User.objects.get(id=user_id)
    RegistrationActivationEmail.objects.create(user=user, activation_key=activation_key)
    current_site = Site.objects.get_current()
    context = {
        'site_domain': current_site.domain,
        'url': reverse('userprofile:activate_email'),
        'email': user.email,
        'code': activation_key,
    }
    subject = render_to_string('send_mail/send_activation_email_subject.txt')
    message = render_to_string('send_mail/send_activation_email.txt', context=context)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])    
