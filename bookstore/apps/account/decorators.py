#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

# ensure_csrf_cookie only in django1.4.2
#from django.views.decorators.csrf import ensure_csrf_cookie
import logging

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

from account.models import EmailSentCount 

log = logging.getLogger("mysite")

def admin_required(func):
    """装饰器: 需要admin权限"""
    def handleAdminAccess(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_superuser:
            return func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("admin_login"))
    
    return handleAdminAccess

def signup_allowed(func):
    """装饰器:
    是否开放注册.
    开放注册，则所有人均可注册。关闭注册，则仅admin登录后可注册
    """
    def handleSignup(request, *args, **kwargs):
        if settings.SIGNUP_ALLOWED or (request.user.is_authenticated() and 
                                       request.user.is_superuser):
            return func(request, *args, **kwargs)
          
        return render_to_response("signup_forbidden.html", RequestContext(request))        
    
    return handleSignup

def login_get_forbidden(func):
    '''装饰器：过滤掉登录后不允许的GET请求'''
    def _forbidden(request, *args, **kwargs):
        if request.method == "GET" and request.user.is_authenticated():
            raise Http404
        
        return func(request, *args, **kwargs)
    return _forbidden
    
def check_email_sent_count(func):
    """装饰器:
        该装饰器用在发送邮件函数(EmailConfirmation.send_confirmation)前.
        发送邮件前需要检测发送次数，以决定是否允许发送邮件. 可以发送, 则发送成功后已发送次数加1
    """
    def _check(*args, **kwargs):
        log.debug("start check email sent count")
        emailAddress=args[1]
        #emailAddress = kwargs.pop("email_address", None)
        try:
            emailSentCount = EmailSentCount.objects.get(email_address=emailAddress.email)
        except EmailSentCount.DoesNotExist:
            emailSentCount = EmailSentCount()
            emailSentCount.email_address = emailAddress.email
            emailSentCount.signup_count = 0
            emailSentCount.reset_pwd_count = 0
            emailSentCount.save()
            
        if emailSentCount.signup_count >= settings.MAX_EMAIL_SENT_COUNT_PERDAY:
            raise Http404
        else:
            func(*args, **kwargs) 
            emailSentCount.signup_count += 1
            emailSentCount.save()
    return _check    
    
def check_reset_email_sent_count(func):
    """装饰器：
        该装饰器用在重置密码邮件发送前
    """
    def _check(*args, **kwargs):
        log.debug("start check reset_email sent count")
        email = args[3]
        try:
            emailSentCount = EmailSentCount.objects.get(email_address=email)
        except EmailSentCount.DoesNotExist:
            raise Http404
        
        if emailSentCount.reset_pwd_count >= settings.MAX_EMAIL_SENT_COUNT_PERDAY:
            raise Http404
        else:
            func(*args, **kwargs)
            emailSentCount.reset_pwd_count += 1
            emailSentCount.save()
    return _check
            
            
            
            
            
