import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from apps.core.tasks import test_task


class TestView(View):

    def get(self, request, *args, **kwargs):
        for i in range(1):
            test_task.delay(5)        
        return HttpResponse(json.dumps({'response': 'We are generating your random users!'}), 
                            content_type='application/json')
