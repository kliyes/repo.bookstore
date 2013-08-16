#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "account.views.signup"
else:
    signup_view = "pinax.apps.signup_codes.views.signup"

urlpatterns = patterns("",
    url(r"^login/$", "account.views.login", name="acct_login"),
    url(r"^signup/$", "account.views.signup", name="acct_signup"),
    url(r"^reset_passwd/$", "account.views.reset_password", name="acct_reset_passwd"),
    url(r"^password_reset/done/$", "account.views.password_reset_done", name="acct_passwd_reset_done"),
    url(r"^password_reset_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", "account.views.password_reset_from_key", name="acct_passwd_reset_key"),
    url(r"^change_password/$", "account.views.password_change", name="acct_change_pwd"),                       
    url(r"^set_password/$", "account.views.password_set", name="set_pwd"),
    url(r"^logout/$", "account.views.logout", {"template_name": "account/logout.html"}, name="acct_logout"),
    url(r"^confirm_email/(\w+)/$", "account.views.confirm_email", name="acct_confirm_email"),
    url(r"^send_confirm_email/$", "account.views.send_confirm_email", name="acct_send_email"),
    url(r"^agreement/$", TemplateView.as_view(template_name="account/agreement.html"), name="acct_agreement"),

    # if we should use post request for safety ?
    url(r"^check_login/$", "account.views.checkIsLogin", name="acct_check_login"),
#    url(r"^isEmailRegistered/$","account.views.isEmailRegistered",name="is_email_registered"),
    
    # 验证码处理
    url(r"^new_secure_code/$","account.views.requestSecureImg",name="new_secure_code"),
    url(r"^check_secure_code/$","account.views.checkSecureCode",name="check_secure_code"),
    
)
