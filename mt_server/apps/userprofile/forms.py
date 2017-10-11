from django import forms
from django.contrib.auth import (get_user_model, authenticate)
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from apps.userprofile.models import UserDetail


User = get_user_model()


class UserCreationCustomForm(UserCreationForm):
    """
    Custom login form. Password does not required.
    Extended user model updated.
    """
    email = forms.EmailField()
    sex = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = forms.ChoiceField(choices=sex, required=True)
    birthday = forms.DateField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'email', 'gender', 'birthday')
        error_messages = {
            'username': {
                'unique': _('User with this username is already exist.'),
            },
        }

    def __init__(self, *args, **kargs):
        super(UserCreationCustomForm, self).__init__(*args, **kargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        del self.fields['password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(_('Email addresses must be unique.'))

        return email

    def clean(self):
        cleaned_data = super(UserCreationCustomForm, self).clean()
        return cleaned_data

    def save(self, commit=True):
        user = super(UserCreationCustomForm, self).save(commit=False)
        user.username = user.username
        user.email = user.email
        user.is_active = False
        user.save()
        parameters = ['gender', 'birthday']
        userprofile = UserDetail.objects.get(user=user)

        for param in parameters:
            setattr(userprofile, param, self.cleaned_data.get(param))

        userprofile.save()
        return user
