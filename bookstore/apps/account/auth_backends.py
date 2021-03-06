#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class AuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        lookup_params = {}
#        if settings.ACCOUNT_EMAIL_AUTHENTICATION:
#            field, identity = "email__iexact", credentials.get("email")
#        else:
#            field, identity = "username__iexact", credentials.get("username")
#        if identity is None:
#            return None

        field, identity = "email__iexact", credentials.get("email", None)
        if not identity:
            field, identity = "username__iexact", credentials.get("username", None) #this if branch just for admin login
        
        lookup_params[field] = identity
        try:
            user = User.objects.get(**lookup_params)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(credentials["password"]):
                return user
    
    def has_perm(self, user, perm):
        # @@@ allow all users to add wiki pages
        wakawaka_perms = [
            "wakawaka.add_wikipage",
            "wakawaka.add_revision",
            "wakawaka.change_wikipage",
            "wakawaka.change_revision"
        ]
        if perm in wakawaka_perms:
            return True
        return super(AuthenticationBackend, self).has_perm(user, perm)


EmailModelBackend = AuthenticationBackend