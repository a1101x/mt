import datetime
import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator 
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _

from apps.userprofile.forms import UserCreationCustomForm
from apps.userprofile.models import UserDetail
from apps.userprofile.utils import (get_form_errors, send_activation_email, send_sms)


User = get_user_model()


class RegistrationView(View):
    form_class = UserCreationCustomForm
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.POST = json.loads(request.body.decode('utf-8'))
        form = UserCreationCustomForm(request.POST)

        if form.is_valid():
            user = form.save()
            phone = request.POST.get('phone', None)

            if phone:
                send_sms(user, phone)
            else:
                msg = _('There is error in phone number.')
                return HttpResponse(json.dumps({'status': 'unsuccess', 'done_message': msg}), 
                                               content_type='application/json')

            msg = _('We\'ve send you sms with code for account activation.')
            return HttpResponse(json.dumps({'status': 'ok', 'done_message': msg}), content_type='application/json')

        errors = get_form_errors(form)
        return HttpResponse(json.dumps({'errors': errors}), content_type='application/json')


class ActivateWithSMSView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ActivateWithSMSView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        request.POST = json.loads(request.body.decode('utf-8'))
        pin_code = request.POST.get('code', None)

        if pin_code:
            user = User.objects.filter(registrationactivationsms__pin_code=pin_code, is_active=False).first()

        validlink = False

        if user:
            validlink = True
            user.is_active = True
            user.save()
            return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
        
        msg = _('The code is wrong. Please check your email to get correct code.')
        return HttpResponse(json.dumps({'status': 'unsuccess',  'done_message': msg}), content_type='application/json')
