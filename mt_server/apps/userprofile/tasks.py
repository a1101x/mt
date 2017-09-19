from celery import task


@task(time_limit=30, default_retry_delay=2, max_retries=5)
def send_sms(user_id, phone):
    pass


@task(time_limit=30, default_retry_delay=2, max_retries=5)
def send_activation_email(user_id, email):
    pass
