from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from cloudinary.models import CloudinaryField

from apps.userprofile.utils import default_time_expired


User = get_user_model()


class UserDetail(models.Model):
    """
    Extended user model.
    mt_workers/apps/userprofile/model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_detail')
    profile_pic = CloudinaryField(_('Profile Picture'), type='private', null=True, blank=True, 
                                  help_text=_('Choice your profile picture.'))
    sex = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(_('Gender'), choices=sex, null=True, max_length=1, help_text=_('Select your gender.'))
    birthday = models.DateField(_('Birthday'), null=True, help_text=_('Enter your date of birth.'))

    class Meta:
        verbose_name = 'UserDetail'
        verbose_name_plural = 'UserDetails'

    def __str__(self):
        return '{}'.format(self.user.username)


@receiver(post_save, sender=User)
def create_or_save_user(sender, instance, created, **kwargs):
    """
    Creating extended user model on default django model save.
    mt_workers/apps/userprofile/model
    """
    if created:
        UserDetail.objects.create(user=instance)
    else:
        instance.user_detail.save()


class RegistrationActivationEmail(models.Model):
    """
    Model for login via email.
    mt_workers/apps/userprofile/model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    activation_key = models.CharField(max_length=40)
    time_expired = models.DateTimeField(default=default_time_expired)

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.activation_key)


class RegistrationActivationSMS(models.Model):
    """
    Model for user activation via sms.
    mt_workers/apps/userprofile/model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    pin_code = models.CharField(max_length=40)
    time_expired = models.DateTimeField(default=default_time_expired)

    def __str__(self):
        return '{} - {}'.format(self.user, self.pin_code)
