from django.contrib.auth import (authenticate, get_user_model)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from apps.userprofile.models import (UserDetail, RegistrationActivationEmail)


User = get_user_model()


class CustomLoginSerializer(LoginSerializer):
    """
    Custom serializer for login, uses 15 minutes password for login.
    """
    def _validate_email(self, email, password):
        user = None

        if email and password:
            try:
                RegistrationActivationEmail.objects.get(user__email=email, activation_key=password,
                                                        time_expired__gt=timezone.now())
                user = authenticate(email=email, password=password)
            except RegistrationActivationEmail.DoesNotExist:
                msg = _('Credentials are not valid.')
                raise ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise ValidationError(msg)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for default django user model.
    """
    profile_pic = serializers.CharField(source='user_detail.profile_pic')
    gender = serializers.CharField(source='user_detail.gender')
    birthday = serializers.DateField(source='user_detail.birthday')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile_pic', 'gender', 'birthday',
                  'is_superuser', 'is_staff', 'is_active', 'last_login', 'date_joined')


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for extended user model.
    """
    class Meta:
        model = UserDetail
        fields = '__all__'


class SendUserActivationSMSSerializer(serializers.Serializer):
    """
    Serializer for sending User activation sms code.
    """
    phone = serializers.CharField()
    user_id = serializers.CharField()


class UserActivationSMSSerializer(serializers.Serializer):
    """
    Serializer for User activation using sms code.
    """
    code = serializers.CharField()
    user_id = serializers.CharField()


class SendLoginEmailSerializer(serializers.Serializer):
    """
    Serializer for sending User email login code.
    """
    email = serializers.CharField()


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=9)
    profile_pic = serializers.CharField(source='user_detail.profile_pic', allow_blank=True)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    gender = serializers.CharField(source='user_detail.gender')
    birthday = serializers.DateField(source='user_detail.birthday')
    phone = serializers.CharField(required=False)

    def create(self, validated_data):
        """
        Creating user profile and extended user model.
        """
        detail = validated_data.pop('user_detail')
        user = User.objects.create(**validated_data)
        user.is_active = False
        user.save()
        instance, created = UserDetail.objects.get_or_create(user=user)

        if not created:
            for key in detail.keys():
                setattr(instance, key, detail[key])
            instance.save()

        return user
