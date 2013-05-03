#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf import settings

from pinax.apps.account.models import Account, AnonymousAccount

def account(request):
    if request.user.is_authenticated():
        try:
            #account = Account.default_manager.get(user=request.user) #commented by jun, no reason
            account = Account.objects.get(user=request.user) 
        except Account.DoesNotExist:
            account = AnonymousAccount(request)
    else:
        account = AnonymousAccount(request)
    return {
        "account": account,
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "support@lianbi.com.cn")
    }
