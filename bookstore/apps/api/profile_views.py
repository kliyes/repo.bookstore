#-*- coding: utf-8 -*-

import random, logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404

from django.contrib.auth.decorators import login_required

from common.utils import jsonResponse
from protocol.decorators import post_request_required, authorized 
from profiles.forms import ProfileForm
from api import errors as err
from api.consts import statusCode


log = logging.getLogger("mysite")


@authorized
@post_request_required
def updateProfile(request):
    """更新用户个人信息设置"""
    
    form = ProfileForm(request.POST, user=request.user)
    if form.is_valid():
        profile = form.save(request)
        if profile is not None:
            return jsonResponse(statusCode(0, "Update profile info successfully"))
        else:
            return jsonResponse(err.PROFILE_UPDATE_ERR)
    else:
        return jsonResponse(err.PROFILE_UPDATE_ERR.format(msg=form.errors))
    



