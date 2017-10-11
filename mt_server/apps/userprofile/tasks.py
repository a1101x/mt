from django.contrib.auth import get_user_model

from celery import task

from apps.userprofile.models import RegistrationActivationEmail


User = get_user_model()


@task(time_limit=10, default_retry_delay=2, max_retries=5, autoretry_for=(Exception,))
def send_sms(user_id, phone):
    """
    mt_workers/apps/userprofile/tasks
    """
    pass


@task(time_limit=10, default_retry_delay=2, max_retries=5, 
      autoretry_for=(User.DoesNotExist, RegistrationActivationEmail.DoesNotExist,))
def send_login_email(user_id, email):
    """
    mt_workers/apps/userprofile/tasks
    """
    pass


@task(time_limit=30, default_retry_delay=15, max_retries=5, autoretry_for=(RegistrationActivationEmail.DoesNotExist,))
def remove_sms_activation_keys():
    """
    mt_workers/apps/userprofile/tasks
    """
    pass


@task(time_limit=300, default_retry_delay=5, max_retries=5, autoretry_for=(Exception,))
def cancel_write_user_consumers():
    """
    mt_workers/apps/userprofile/tasks
    """
    pass
    