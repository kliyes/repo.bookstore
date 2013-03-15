# -*-coding:utf-8 -*-
'''
Created on Jul 30, 2012

@author: junn
'''
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.contrib import messages
from django.core.urlresolvers import reverse 

from onlineuser.models import getOnlineInfos
from onlineuser.models import Online

from common import utils
from account.forms import LoginForm
from account.decorators import admin_required
from sites.forms import FeedbackForm
from sites.models import Feedback 

import logging
log = logging.getLogger("mysite")

@admin_required
def getOnlines(request):
    onlineInfos = getOnlineInfos(detail=False)
    onlineInfos["online_users"] = Online.objects.onlines()
    return render_to_response("site/onlineinfos.html",
        RequestContext(request,onlineInfos))

@admin_required
def viewFeedbacks(request):
    return render_to_response(
        "site/view_feedbacks.html", 
        RequestContext(request,{"feeds": Feedback.objects.getAllFeedbacks(),})) 
    

def submitFeedback(request):
    if request.POST:
        form = FeedbackForm(request.POST)
        if form.is_valid():
            profile = None
            if request.user.is_authenticated():
                profile = request.user.get_profile()  
            feed = form.save(profile) 
            utils.addMsg(request, messages.SUCCESS, u"意见提交成功，我们会尽快做出处理，谢谢关注！")
            
            return HttpResponseRedirect(reverse("us_feedback"))  
    else:
        form = FeedbackForm()
        
    return render_to_response(settings.TEMPLATE_FEEDBACK, RequestContext(request,{'form':form,}))


def siteAnnouncement(request):
    if settings.SITE_MAINTAINED:
        return direct_to_template(request, template="555.html")
    
    raise Http404
