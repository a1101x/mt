from celery import task


@task(time_limit=30, default_retry_delay=10, max_retries=5)
def test_task(total):
    pass
