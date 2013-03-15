# -*-coding:utf-8 -*-

'''
Created on Feb 12, 2012

@author: junn
'''

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import EmailMessage
from django.core.mail import send_mail  
from django.conf import settings
from django.template import loader  
from django.views.generic.simple import direct_to_template
from django.utils import simplejson as json
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache  

from common.utils import jsonResponse 

#from diary.models import Diary

def test(request):
    return render_to_response("tests/login1.html", RequestContext(request, {"hehe":"hello"}))


def clearCache(request):
    cache.clear()
    print '======== Cache cleared ========='
    return HttpResponse("Cache cleared")

def getUserinfo(request):
    return render_to_response("tests/userinfo.html", RequestContext(request,))

# only used for testing, don't delete this code
def myLogout(request, **kwargs):
    request.session.flush() # clear session
    request.user = AnonymousUser()
    return HttpResponse("Logged out")

def testAjax(request):
    if request.is_ajax():
        return HttpResponse(json.dumps({"status": "success", "html": "<span>Hello kitty</span>"}))
    
    return HttpResponse(json.dumps({"status": "error",})) 

def direct2template(request):
    return direct_to_template(request, "404.html")

  
def sendEmail(request):
#    send_mail('subject','body',settings.EMAIL_HOST_USER, ['xjbean@qq.com'],fail_silently=True)
    
    subject = u'这封邮件来自'  
    html_content = loader.render_to_string("tests/confirm_email.html",{"site":"www.zongsui.com",})  
    recipient_list = [
        "xjbean@qq.com", 
    ]
  
    msg = EmailMessage(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)  
    msg.content_subtype = "html"   
    msg.send()  
    
    return HttpResponseRedirect(request.GET.get("next"))
  



