#-*- coding: utf-8 -*-

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from common.utils import jsonResponse
from protocol.decorators import post_request_required, authorized 
from activity.models import Activity
from api import errors as err
from api.consts import statusCode

import logging
log = logging.getLogger("mysite")


@authorized
def detailActivity(request):
    """获取活动详情 """
    activityId = request.GET.get("activityId", None)
    try:
        activity = Activity.objects.get(id=activityId)
        return jsonResponse({"activity":activity.toJson()})
    except Activity.DoesNotExist:
        log.debug("Activity with id %s is not exist" % activityId)
        return jsonResponse(err.ACTIVITY_NOT_EXIST.format(activityId))

    return jsonResponse(err.ACTIVITY_DETAIL_ERR.format(activityId))

@authorized
@post_request_required
@login_required
def joinActivity(request):
    """参加活动API处理函数"""
    activityId = request.POST.get("activityId", None)
    try:
        act = Activity.objects.get(id=activityId)
        if request.user.get_profile().joinActivity(act):
            return jsonResponse(statusCode(0, "join activity %s successfully" % act.id))
        else:
            return jsonResponse(err.ACTIVITY_JOIN_ERR.format(activityId))
    except Activity.DoesNotExist:
        log.debug("Activity with id %s is not exist in attendActivity()" % activityId)
        return jsonResponse(err.ACTIVITY_NOT_EXIST.format(activityId)) 
     
     
