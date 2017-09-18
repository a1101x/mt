from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from apps.userprofile.models import UserDetail


admin.site.unregister(User)


class UserDetailInline(admin.StackedInline):
    model = UserDetail


class ExtendUserAdmin(UserAdmin):
    inlines = [UserDetailInline]


class UserDetailAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Personal'), {'fields': ('birthday', 'gender',)}),
    )
    list_display = ['user', 'gender']
    list_filter = ['gender']
    search_fields = ['user__email', 'user__username']
    ordering = ['user__username']


admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(User, ExtendUserAdmin)
