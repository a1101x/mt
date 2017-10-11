from django.contrib.auth import get_user_model

from celery import task


User = get_user_model()


@task(time_limit=30, default_retry_delay=10, max_retries=5, autoretry_for=(User.DoesNotExist,))
def test_task(total):
    """
    mt_workers/apps/core/tasks
    """
    pass


@task(time_limit=1, default_retry_delay=1, max_retries=10, queue='elastic_read_user', autoretry_for=(Exception,))
def elastic_read_user(index, doc_type, _id):
    """
    mt_workers/apps/core/tasks
    """
    pass


@task(time_limit=25, default_retry_delay=1, max_retries=5, autoretry_for=(Exception,))
def elastic_write_user(index, doc_type, _id, body):
    """
    mt_workers/apps/core/tasks
    """
    pass
