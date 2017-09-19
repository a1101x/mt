from django.conf.urls import url, include

from refreshtoken.routers import urlpatterns as rt_urlpatterns

from apps.userprofile.views import RegistrationView, ActivateWithSMSView


urlpatterns = [
    url(r'^registration/$', RegistrationView.as_view()),
    url(r'^activate_sms/$', ActivateWithSMSView.as_view(), name='activate_sms'),
    url(r'^auth/', include('rest_auth.urls')),
] + rt_urlpatterns
