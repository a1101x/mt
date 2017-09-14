from django.conf.urls import url

from apps.core.views import GenerateRandomUserView

urlpatterns = [
    url(r'^users/$', GenerateRandomUserView.as_view(), name='randomusers'),        
]
