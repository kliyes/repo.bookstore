#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import re
from timezones.forms import TimeZoneField

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.http import int_to_base36

from account.signals import signedup
from account.models import Account, PasswordReset, EmailAddress, EmailConfirmation
from account.utils import perform_login, change_password
from account.decorators import check_reset_email_sent_count
from books.models import Cart
from common.utils import ecode
from common import utils 
from profiles.models import Profile, City

alnum_re = re.compile(r"^\w+$")

# @@@ might want to find way to prevent settings access globally here.
REQUIRED_EMAIL = getattr(settings, "ACCOUNT_REQUIRED_EMAIL", False)
EMAIL_VERIFICATION = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", False)
EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", False)


class GroupForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop("group", None)
        super(GroupForm, self).__init__(*args, **kwargs)


class LoginForm(GroupForm):
    email = forms.EmailField(
        required = True,
        widget=forms.TextInput() 
    )
    
    password = forms.CharField(widget = forms.PasswordInput(render_value=False))
    
    remember = forms.BooleanField(required = False)
    
    user = None
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["password"].initial = ""
        
        ordering = []
        if EMAIL_AUTHENTICATION:
            self.fields["email"] = forms.EmailField()
            ordering.append("email")
        ordering.extend(["password", "remember"])
        self.fields.keyOrder = ordering
        
    
    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {}
        if EMAIL_AUTHENTICATION:
            credentials["email"] = self.cleaned_data["email"]
        else:
            credentials["username"] = self.cleaned_data["username"]
        credentials["password"] = self.cleaned_data["password"]
        return credentials
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        if UNIQUE_EMAIL or EMAIL_AUTHENTICATION:
            try:
                user = User.objects.get(email__iexact=value)
            except User.DoesNotExist:
                raise forms.ValidationError(_(u"Email账号不存在"))
            
            if user:
                if not user.is_active:
                    raise forms.ValidationError(_(u"该Email账号尚未激活"))
        return value

    def clean_password(self):
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if not user:
            raise forms.ValidationError(_(u"密码不正确"))
        
        return self.cleaned_data["password"]
    
    def clean(self):
        """Following code is needed, we can't remove it!!!"""
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("账号未激活."))
        else:
            if EMAIL_AUTHENTICATION:
                error = _("The email address and/or password you specified are not correct.")
            else:
                error = _("The username and/or password you specified are not correct.")
            raise forms.ValidationError(error)
        return self.cleaned_data
    
    def login(self, request):
        perform_login(request, self.user)
        
        if self.cleaned_data["remember"]:
            request.session.set_expiry(60 * 60 * 24 * 7 * 3)
        else:
            request.session.set_expiry(0)


class SignupForm(GroupForm):
    email = forms.EmailField(widget=forms.TextInput(),required = True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    nickname = forms.CharField(widget=forms.TextInput(), required=True)
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        if UNIQUE_EMAIL or EMAIL_AUTHENTICATION:
            try:
                user = User.objects.get(email__iexact=value)
                if not user.is_active:
                    return value 
            except User.DoesNotExist:
                return value
            raise forms.ValidationError(_(u"该Email已被注册"))
        return value
    
    def clean_password(self):
        pwd = self.cleaned_data["password"]
        if len(pwd) < 6:
            raise forms.ValidationError(_(u"密码长度应不少于6个字符"))
        return pwd
    
    # TODO nickname is required
    def clean_nickname(self):
        nick = self.cleaned_data["nickname"]
    
        if not nick or len(nick.strip()) <= 0:
            raise forms.ValidationError(_(u"昵称不能为空"))
        if len(ecode(nick.strip())) > 14 or len(ecode(nick.strip())) < 4:
            raise forms.ValidationError(_(u"昵称为4-14个英文字符或2-7个汉字"))
        return nick.strip()
    
    def clean(self):
        return self.cleaned_data
    
    def get_or_create_user(self, commit=True):
        """ 若email已注册过但未激活，则取出已注册记录更新 """
        email = self.cleaned_data["email"].strip().lower()
        
        user = None
        try:
            #前面已做验证，若存在email已激活且被注册，则不会走到此
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = User()
            user.email = email

        user.username = user.email;
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user
    
    def login(self, request, user):
        # nasty hack to get get_user to work in Django
        user.backend = "django.contrib.auth.backends.ModelBackend"
        perform_login(request, user)
    
    def save(self, request=None):
        email = self.cleaned_data["email"]
        new_user = self.get_or_create_user(True)
        emailAddress = EmailAddress.objects.add_email(new_user, email)  # just only add email address,
        self.after_signup(request, new_user, emailAddress)
        
        return new_user, emailAddress
    
    #mainly create profile entity
    def after_signup(self, request, user, emailAddress, **kwargs):
        profile = None
        
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile(user=user)
        
        profile.name = self.cleaned_data.get("nickname")
        profile.city = City.objects.getById(id=2)  #TODO, load from cities cache
        profile.save()
        
        #=======================================================
        #code in the bookstore
        '''为注册用户创建购物车'''
        try:
            cart = Cart.objects.get(owner=profile)
        except Cart.DoesNotExist:
            cart = Cart(owner=profile)
        
        cart.save()
        #=======================================================

class OpenIDSignupForm(SignupForm):
    
    def __init__(self, *args, **kwargs):
        # remember provided (validated!) OpenID to attach it to the new user
        # later.
        self.openid = kwargs.pop("openid", None)
        # pop these off since they are passed to this method but we can't
        # pass them to forms.Form.__init__
        kwargs.pop("reserved_usernames", [])
        kwargs.pop("no_duplicate_emails", False)
        
        super(OpenIDSignupForm, self).__init__(*args, **kwargs)
        
        # these fields make no sense in OpenID
        del self.fields["password1"]
        del self.fields["password2"]


class UserForm(forms.Form):
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AccountForm(UserForm):
    
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        try:
            self.account = Account.objects.get(user=self.user)
        except Account.DoesNotExist:
            self.account = Account(user=self.user)


class AddEmailForm(UserForm):
    
    email = forms.EmailField(
        label = _("Email"),
        required = True,
        widget = forms.TextInput(attrs={"size": "30"})
    )
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        errors = {
            "this_account": _("This email address already associated with this account."),
            "different_account": _("This email address already associated with another account."),
        }
        if UNIQUE_EMAIL:
            try:
                email = EmailAddress.objects.get(email__iexact=value)
            except EmailAddress.DoesNotExist:
                return value
            if email.user == self.user:
                raise forms.ValidationError(errors["this_account"])
            raise forms.ValidationError(errors["different_account"])
        else:
            try:
                EmailAddress.objects.get(user=self.user, email__iexact=value)
            except EmailAddress.DoesNotExist:
                return value
            raise forms.ValidationError(errors["this_account"])
    
    def save(self):
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])


class ChangePasswordForm(UserForm):
    
    oldpassword = forms.CharField(
        widget = forms.PasswordInput(render_value=False, attrs={"id":"old-password"})
    )
    password1 = forms.CharField(
        widget = forms.PasswordInput(render_value=False, attrs={"id":"new-password"})
    )
    password2 = forms.CharField(
        widget = forms.PasswordInput(render_value=False, attrs={"id":"repeat-password"})
    )
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_(u"原密码输入错误."))
        return self.cleaned_data["oldpassword"]
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_(u"请确保两次输入密码相同."))
        return self.cleaned_data["password2"]
    
    def save(self):
        change_password(self.user, self.cleaned_data["password1"])


class SetPasswordForm(UserForm):
    
    password1 = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


from account.threads import startEmailSendThread
class ResetPasswordForm(forms.Form):
    
    email = forms.EmailField(
        required = True,
        widget = forms.TextInput()
    )
    
    def clean_email(self):
        if EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"], verified=True).count() == 0:
            raise forms.ValidationError(_(u"该Email账号尚未激活"))
        return self.cleaned_data["email"]
    
    @check_reset_email_sent_count
    def send_reset_email(self, subject, message, email):
        startEmailSendThread(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    
    def save(self, **kwargs):
        
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)
        
        for user in User.objects.filter(email__iexact=email):
            
            temp_key = token_generator.make_token(user)
            
            # save it to the password reset model
            password_reset = PasswordReset(user=user, temp_key=temp_key)
            password_reset.save()
            
            current_site = Site.objects.get_current()
            domain = unicode(current_site.domain)
            
            # send the password reset email
            subject = settings.PASSWD_RESET_SUBJECT
            message = render_to_string(settings.PWD_RESET_MSG, {
                "user": user,
                "uid": int_to_base36(user.id),
                "temp_key": temp_key,
                "domain": domain,
            })
            
            self.send_reset_email(subject, message, user.email)
            # launch a new thread to send email, don't let users wait for so long, by junn
            #startEmailSendThread(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return self.cleaned_data["email"]


class ResetPasswordKeyForm(forms.Form):
    
    password1 = forms.CharField(
        label = _(u"新密码"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _(u"再次输入新密码"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
    
    def clean_password1(self):
        if len(self.cleaned_data["password1"]) < 6:
                raise forms.ValidationError(_(u"密码长度应不少于6个字符"))
            
        return self.cleaned_data["password1"]    
            
    def clean_password2(self):
        if len(self.cleaned_data["password2"]) < 6:
                raise forms.ValidationError(_(u"密码长度应不少于6个字符"))
            
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_(u"两次输入密码必须相同."))
            
        return self.cleaned_data["password2"]
    
    def save(self):
        # set the new user password
        user = self.user
        user.set_password(self.cleaned_data["password1"])
        user.save()
        # mark password reset object as reset
        PasswordReset.objects.filter(temp_key=self.temp_key).update(reset=True)


class ChangeTimezoneForm(AccountForm):
    
    timezone = TimeZoneField(label=_("Timezone"), required=True)
    
    def __init__(self, *args, **kwargs):
        super(ChangeTimezoneForm, self).__init__(*args, **kwargs)
        self.initial.update({"timezone": self.account.timezone})
    
    def save(self):
        self.account.timezone = self.cleaned_data["timezone"]
        self.account.save()


class ChangeLanguageForm(AccountForm):
    
    language = forms.ChoiceField(
        label = _("Language"),
        required = True,
        choices = settings.LANGUAGES
    )
    
    def __init__(self, *args, **kwargs):
        super(ChangeLanguageForm, self).__init__(*args, **kwargs)
        self.initial.update({"language": self.account.language})
    
    def save(self):
        self.account.language = self.cleaned_data["language"]
        self.account.save()

#class DiaryAdminAuthenticationForm(AuthenticationForm):
#    """
#    A custom authentication form used in the admin app.
#
#    """
#    this_is_the_login_form = forms.BooleanField(widget=forms.HiddenInput, initial=1,
#        error_messages={'required': ugettext_lazy("Please log in again, because your session has expired.")})

