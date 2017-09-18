import hashlib
import random
import string

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from refreshtoken.models import RefreshToken

from apps.userprofile.models import RegistrationActivationEmail


def generate_code():
    secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
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
