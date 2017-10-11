from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view


schema_view = get_swagger_view(title='API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^ht/', include('health_check.urls')),
    url(r'^api/v1/', include('apps.userprofile.urls', namespace='userprofile')),
    url(r'^api/v1/', include('apps.core.urls', namespace='core')),
    url(r'^docs/', schema_view),
]
