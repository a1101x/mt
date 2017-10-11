from datetime import timedelta
from random import choice
import string

from django.utils import timezone

from refreshtoken.models import RefreshToken


def get_form_errors(form):
    """
    Check form errors.
    """
    errors = {}
    for key, value in form.errors.items():
        messages = []
        for message in value:
            messages.append(message)
        errors[key] = messages
    return errors


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Adding refresh_token to jwt response.
    """
    payload = {'token': token,}
    app = 'mt'

    try:
        refresh_token = user.refresh_tokens.get(app=app).key
    except RefreshToken.DoesNotExist:
        refresh_token = None

    payload['refresh_token'] = refresh_token
    return payload


def default_time_expired():
    """
    Key lifetime.
    """
    time = timezone.now() + timedelta(minutes=15)
    return time


def generate_code():
    """
    Generate random alphanumeric code.
    """
    secret = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(9))
    return secret
