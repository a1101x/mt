from django.conf.urls import url

from apps.core.views import TestView

urlpatterns = [
    url(r'^test/$', TestView.as_view(), name='test'),        
]
