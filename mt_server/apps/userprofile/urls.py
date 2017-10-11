from django.conf.urls import url, include

from refreshtoken.routers import urlpatterns as rt_urlpatterns

from apps.userprofile.views import (RegistrationView, SendUserSMSActivationViewSet, UserSMSActivationViewSet,
                                    SendLoginEmailViewSet, CurrentUserViewSet, UserProfileListViewSet,
                                    UserProfileViewSet, UserDetailListViewSet, UserDetailViewSet,
                                    UserRegistrationViewSet)


urlpatterns = [
    url(r'^user/registration/$', UserRegistrationViewSet.as_view()),
    url(r'^user/send_activation_sms/', SendUserSMSActivationViewSet.as_view()),
    url(r'^user/activate_sms/$', UserSMSActivationViewSet.as_view()),
    url(r'^user/send_login_email/$', SendLoginEmailViewSet.as_view()),
    url(r'^user/currentuser/$', CurrentUserViewSet.as_view()),
    url(r'^user/userprofile/$', UserProfileListViewSet.as_view()),
    url(r'^user/userprofile/(?P<pk>[0-9]+)/$', UserProfileViewSet.as_view()),
    url(r'^user/userdetail/$', UserDetailListViewSet.as_view()),
    url(r'^user/userdetail/(?P<pk>[0-9]+)/$', UserDetailViewSet.as_view()),
    url(r'^user/', include('rest_auth.urls')),
    url(r'^user/', include(rt_urlpatterns)),
]
