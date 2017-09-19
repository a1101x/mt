import hashlib
from random import randrange, shuffle, choice
import string

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from twilio.rest import Client
from refreshtoken.models import RefreshToken

from apps.userprofile.models import RegistrationActivationEmail, RegistrationActivationSMS


def generate_pin_code():
    secret = list(randrange(0,9) for _ in range(4))
    shuffle(secret)
    return "".join(map(str, secret))


def generate_code():
    secret = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(9))
    return secret


def send_activation_email(user, email):
    activation_key = generate_code()
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


def get_form_errors(form):
    errors = {}
    for key, value in form.errors.items():
        messages = []
        for message in value:
            messages.append(message)
        errors[key] = messages
    return errors


def jwt_response_payload_handler(token, user=None, request=None):
    payload = {'token': token,}
    app = 'mt'

    try:
        refresh_token = user.refresh_tokens.get(app=app).key
    except RefreshToken.DoesNotExist:
        refresh_token = None

    payload['refresh_token'] = refresh_token
    return payload


def send_sms(user, phone):
    pin_code = generate_pin_code()
    RegistrationActivationSMS.objects.create(user=user, pin_code=pin_code)
    context = {
        'code': pin_code,
    }

    message = render_to_string('send_sms/send_email_activation_sms.txt', context=context)
    message = message.encode('utf-8')
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    response = client.messages.create(body=message, to=phone, from_=settings.TWILIO_NUMBER)
    return response
