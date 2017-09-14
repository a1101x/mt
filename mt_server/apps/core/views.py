import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from .tasks import create_random_user_accounts


class GenerateRandomUserView(View):

    def get(self, request, *args, **kwargs):
        create_random_user_accounts.delay(1)
        return HttpResponse(json.dumps(
                                {
                                    'response': 'We are generating your random users!'
                                }
                            ), content_type='application/json')
