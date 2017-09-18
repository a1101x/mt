from django.conf.urls import url, include

from refreshtoken.routers import urlpatterns as rt_urlpatterns

from apps.userprofile.views import RegistrationView, ActivateEmailView


urlpatterns = [
    url(r'^registration/$', RegistrationView.as_view()),
    url(r'^activate_email/$', ActivateEmailView.as_view(), name='activate_email'),
    url(r'^auth/', include('rest_auth.urls')),
] + rt_urlpatterns
