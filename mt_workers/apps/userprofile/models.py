from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from cloudinary.models import CloudinaryField


User = get_user_model()


class UserDetail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    profile_pic = CloudinaryField(_('Profile Picture'), null=True, blank=True, 
                                  help_text='Choice your profile picture.')
    sex = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(_('Gender'), choices=sex, null=True, max_length=1, help_text='Select your gender.')
    birthday = models.DateField(_('Birthday'), null=True, help_text='Enter your date of birth.')

    class Meta:
        verbose_name = 'UserDetail'
        verbose_name_plural = 'UserDetails'

    def __str__(self):
        return '{}'.format(self.user.username)


@receiver(post_save, sender=User)
def create_or_save_user(sender, instance, created, **kwargs):
    if created:
        UserDetail.objects.create(user=instance)
    else:
        instance.userdetail.save()


class RegistrationActivationEmail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    activation_key = models.CharField(max_length=40)

    def __str__(self):
        return '{}'.format(self.user.email)


class RegistrationActivationSMS(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    pin_code = models.CharField(max_length=40)

    def __str__(self):
        return '{} - {}'.format(self.user, self.pin_code)
