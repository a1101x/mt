from datetime import timedelta
from random import randrange, shuffle, choice
import string

from django.utils import timezone


def generate_pin_code():
    """
    Generate 4 digit pin-code.
    """
    secret = list(randrange(0, 9) for _ in range(4))
    shuffle(secret)
    return ''.join(map(str, secret))


def generate_code():
    """
    Generate random alphanumeric code.
    """
    secret = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(9))
    return secret


def default_time_expired():
    """
    mt_server/apps/userprofile/utils
    """
    time = timezone.now() + timedelta(minutes=15)
    return time
