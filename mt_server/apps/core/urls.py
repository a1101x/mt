from django.conf.urls import url

from apps.core.views import (TestViewSet, WorkersViewSet, CancelConsumer)


urlpatterns = [
    url(r'^core/test/$', TestViewSet.as_view()),
    url(r'^core/worker/', WorkersViewSet.as_view()),
    url(r'^core/cancel_consumer/', CancelConsumer.as_view()),
]
