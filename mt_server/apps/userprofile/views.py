import json
import socket

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import View

from rest_framework import (generics, mixins, viewsets)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from celery import current_app

from apps.core.tasks import elastic_write_user
from apps.userprofile.decorators import CSRFExemptMixin
from apps.userprofile.forms import UserCreationCustomForm
from apps.userprofile.models import (UserDetail, RegistrationActivationSMS, RegistrationActivationEmail)
from apps.userprofile.serializers import (UserProfileSerializer, UserDetailSerializer, SendUserActivationSMSSerializer, 
                                          UserActivationSMSSerializer, SendLoginEmailSerializer,
                                          UserRegistrationSerializer)
from apps.userprofile.tasks import (send_sms, send_login_email)
from apps.userprofile.utils import (get_form_errors, generate_code)


User = get_user_model()


class RegistrationView(CSRFExemptMixin, View):
    """
    View for new user registration.
    """
    form_class = UserCreationCustomForm
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        # Register new user.

        parameters:
            - name: username
              description: username
              required: true
              type: string
            - name: email
              description: email
              required: true
              type: string
            - name: gender
              description: gender
              required: true
              type: string
            - name: birthday
              description: birthday
              required: true
              type: string
            - name: phone
              description: phone
              required: true
              type: string

        responseMessages:
            - code: 200
              message: We have sent you sms with code for account activation. Code is valid only for 15 minutes!
            - code: 400
              message: There is error in phone number.
            - code: 400
              message: form errors

        consumes:
            - application/json

        produces:
            - application/json
        """
        request.POST = json.loads(request.body.decode('utf-8'))
        form = UserCreationCustomForm(request.POST)

        if form.is_valid():
            user = form.save()
            phone = request.POST.get('phone', None)

            if phone:
                send_sms.delay(user.id, phone)
            else:
                return HttpResponse(json.dumps({
                    'status': 'unsuccess',
                    'detail': _('There is error in phone number.')
                }), status=400, content_type='application/json')

            return HttpResponse(json.dumps({
                'status': 'success',
                'user_id': user.id,
                'detail': _('We have sent you sms with code for account activation.'
                            ' Code is valid only for 15 minutes!')
            }), content_type='application/json')

        errors = get_form_errors(form)
        return HttpResponse(json.dumps({
            'status': 'unsuccess', 
            'errors': errors
        }), status=400, content_type='application/json')


class CurrentUserViewSet(generics.GenericAPIView):
    """
    get:
        Return a detailed user profile.
    """
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class UserProfileListViewSet(mixins.ListModelMixin, generics.GenericAPIView):
    """
    list:
        Return a list of user profiles.
    """
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        return User.objects.all()

    def get(self, request, *args, **kwargs):
        """
        # Get list of user profiles.
        """
        return self.list(request, *args, **kwargs)


class UserProfileViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    """
    retrieve:
        Return a user profiles.
    """
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        return User.objects.all()

    def get(self, request, *args, **kwargs):
        """
        # Get user profile by id.
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        # Update user profile (partial=true).
        """
        return self.partial_update(request, *args, **kwargs)


class UserDetailListViewSet(mixins.ListModelMixin, generics.GenericAPIView):
    """
    list:
        Return a list of user details.
    """
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        return UserDetail.objects.all()

    def get(self, request, *args, **kwargs):
        """
        # Get list of user detail profiles.
        """
        return self.list(request, *args, **kwargs)


class UserDetailViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        generics.GenericAPIView):
    """
    retrieve:
        Return a detailed user info.

    create:
        Add a new user detailed profile.

    partial_update:
        Update/edit selected user detailed profile.
    """
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        return UserDetail.objects.all()

    def get(self, request, *args, **kwargs):
        """
        # Get user detail profile by id.
        """
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        # Create user detail profile by id.
        """
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        # Update user detail profile (partial=true).
        """
        return self.partial_update(request, *args, **kwargs)


class SendUserSMSActivationViewSet(generics.GenericAPIView):
    """
    post:
        Send sms code for user activation.
    """
    serializer_class = SendUserActivationSMSSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        """
        # Send sms code for selected user.
        """
        phone = request.data.get('phone', None)
        user_id = request.data.get('user_id', None)
        serializer = SendUserActivationSMSSerializer(data={
            'phone': phone,
            'user_id': user_id
        })

        if serializer.is_valid():
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError({
                    'status': 'unsuccess',
                    'detail': _('User with this id does not exist.')
                })

            if not user.is_active:
                try:
                    RegistrationActivationSMS.objects.filter(user=user_id, user__is_active=False).delete()
                except RegistrationActivationSMS.DoesNotExist:
                    pass
                send_sms.delay(user_id, phone)
            else:
                raise ValidationError({
                    'status': 'unsuccess',
                    'detail': _('User account is already activated.')
                })

            return Response({
                'status': 'success',
                'detail': _('We have sent you sms with code for account activation.'
                            ' Code is valid only for 15 minutes!')
            }, status=HTTP_200_OK)
        else:
            raise ValidationError({
                'status': 'unsuccess',
                'errors': serializer.errors
            })


class UserSMSActivationViewSet(generics.GenericAPIView):
    """
    post:
        Activate user with sms code.
    """
    serializer_class = UserActivationSMSSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        """
        # Activate new user using sms code.
        """
        code = request.data.get('code', None)
        user_id = request.data.get('user_id', None)
        serializer = UserActivationSMSSerializer(data={'code': code, 'user_id': user_id})

        if serializer.is_valid():
            try:
                code = RegistrationActivationSMS.objects.get(user=user_id, pin_code=code, user__is_active=False,
                                                             time_expired__gt=timezone.now())
            except RegistrationActivationSMS.DoesNotExist:
                raise ValidationError({
                    'status': 'unsuccess',
                    'detail': _('Mathing query does not exists or, maybe, code is already expired.')
                })

            if code.user:
                code.user.is_active = True
                code.user.save()
                code.delete()
                serializer = UserProfileSerializer(code.user)
                data = serializer.data
                queue = 'write_user_' + str(code.user_id)
                current_app.control.add_consumer(
                    queue=queue, 
                    exchange='elastic_write_user', 
                    exchange_type='direct', 
                    reply=True, 
                    destination=['elastic_write_user@{}'.format(socket.gethostname())],
                )
                elastic_write_user.apply_async(['users', 'userprofile', code.user_id, data], queue=queue, 
                                               routing_key=queue)
                return Response({
                    'status': 'success',
                    'detail': _('Account is activated.')
                }, status=HTTP_200_OK)
        else:
            raise ValidationError({
                'status': 'unsuccess', 
                'errors': serializer.errors
            })


class SendLoginEmailViewSet(generics.GenericAPIView):
    """
    post:
        Send email code for user login.
    """
    serializer_class = SendLoginEmailSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        """
        # Send email code for user login.
        """
        email = request.data.get('email', None)
        serializer = SendLoginEmailSerializer(data={'email': email})

        if serializer.is_valid():
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError({
                    'status': 'unsuccess', 
                    'detail': _('User with this email does not exist.')
                })
            
            if not user.is_active:
                raise ValidationError({
                    'status': 'unsuccess',
                    'detail': _('User is not activated yet. You should actvate your account first.')
                })

            try:
                RegistrationActivationEmail.objects.filter(user=user).delete()
            except RegistrationActivationEmail.DoesNotExist:
                pass

            send_login_email.delay(user.id, email)
            return Response({
                'status': 'success',
                'email': email,
                'detail':  _('We have sent you email with code for login. Code is valid only for 15 minutes!'),
            }, status=HTTP_200_OK)
        else:
            raise ValidationError({
                'status': 'unsuccess', 
                'errors': serializer.errors
            })     


class UserRegistrationViewSet(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    post:
        Register new user.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        """
        # Register new user.
        """
        username = request.data.get('username', None)
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', None)
        profile_pic = request.data.get('profile_pic', '')
        gender = request.data.get('gender', None)
        birthday = request.data.get('birthday', None)
        phone = request.data.get('phone', None)
        password = make_password(generate_code())
        serializer = UserRegistrationSerializer(data={
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'profile_pic': profile_pic,
            'gender': gender,
            'birthday': birthday,
        })

        if serializer.is_valid():
            user = serializer.save()

            try:
                send_sms.delay(user.id, phone)
            except:
                raise ValidationError({
                    'status': 'unsuccess',
                    'detail': _('Error during SMS send.')
                })

            return Response({
                'status': 'success',
                'user_id': user.id,
                'detail': _('We have sent you sms with code for account activation.'
                            ' Code is valid only for 15 minutes!')
            }, status=HTTP_200_OK)
        else:
            raise ValidationError({
                'status': 'unsuccess',
                'errors': serializer.errors
            })
