#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from profiles.models import Profile

def get_profile(request):
    user = request.user
    if user.is_authenticated():
        try:
            profile  = user.get_profile()
        except Profile.DoesNotExist:    
            profile = Profile(user=user, name=user.username)
            profile.save()
    else:
        profile = "Anonymous"    
    
    return {
        "profile": profile,
    }    
    
def getNoticeCount(request):
    return  {}