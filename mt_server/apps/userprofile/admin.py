from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from refreshtoken.models import RefreshToken

from apps.userprofile.models import (UserDetail, RegistrationActivationSMS, RegistrationActivationEmail)


admin.site.unregister(User)


class UserDetailInline(admin.StackedInline):
    """
    Adding extended user model to default django user model.
    """
    model = UserDetail


class ExtendUserAdmin(UserAdmin):
    """
    Adding extended user model to default django user model.
    """
    inlines = [UserDetailInline]


class UserDetailAdmin(admin.ModelAdmin):
    """
    Displaying the model in the admin panel
    """
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Personal'), {'fields': ('birthday', 'gender',)}),
    )
    list_display = ['user', 'gender']
    list_filter = ['gender']
    search_fields = ['user__email', 'user__username']
    ordering = ['user__username']


class RegistrationActivationSMSAdmin(admin.ModelAdmin):
    """
    Displaying the model in the admin panel
    """
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Code'), {'fields': ('pin_code', 'time_expired',)}),
    )
    list_display = ['user', 'pin_code', 'time_expired']
    search_fields = ['user__email', 'user__username']
    ordering = ['user__username']


class RegistrationActivationEmailAdmin(admin.ModelAdmin):
    """
    Displaying the model in the admin panel
    """
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Code'), {'fields': ('activation_key', 'time_expired',)}),
    )
    list_display = ['user', 'activation_key', 'time_expired']
    search_fields = ['user__email', 'user__username']
    ordering = ['user__username']


class RefreshTokenAdmin(admin.ModelAdmin):
    """
    Displaying the model in the admin panel
    """
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Code'), {'fields': ('key', 'app',)}),
        (_('Created'), {'fields': ('created',)}),
    )
    list_display = ['user', 'key', 'app']
    readonly_fields = ['created',]
    search_fields = ['user__email', 'user__username', 'app']
    ordering = ['user__username', 'app', 'created']


admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(User, ExtendUserAdmin)
admin.site.register(RegistrationActivationSMS, RegistrationActivationSMSAdmin)
admin.site.register(RegistrationActivationEmail, RegistrationActivationEmailAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)
