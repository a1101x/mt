import string

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.crypto import get_random_string

from celery import task


@task(time_limit=30, default_retry_delay=60, max_retries=5)
def create_random_user_accounts(total):
    try:
        for i in range(total):
            username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
            email = '{}@example.com'.format(username)
            password = get_random_string(50)
            User.objects.create_user(username=username, email=email, password=password)

            user = User.objects.get(username=username, email=email)
            cache.set(user.id, user, timeout=3600)

            User.objects.get(username=username, email=email).delete()
        return '{} random users created with success!'.format(total)
    except User.DoesNotExist:
        create_random_user_accounts.retry()
