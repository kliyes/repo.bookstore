from django.contrib import admin

from pinax.apps.account.models import Account, PasswordReset


class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ["user", "temp_key", "timestamp", "reset"]

from django import forms

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy, ugettext as _

ERROR_MESSAGE = ugettext_lazy("Please enter a correct username and password. "
                              "Note that both fields are case-sensitive.")


admin.site.register(Account)
admin.site.register(PasswordReset, PasswordResetAdmin)