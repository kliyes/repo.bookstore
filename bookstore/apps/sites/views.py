# -*-coding:utf-8 -*-
'''
Created on Jul 30, 2012

@author: junn
'''
from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.contrib import messages
from django.core.urlresolvers import reverse 
from django.utils import simplejson

from onlineuser.models import getOnlineInfos
from onlineuser.models import Online

from common import utils
from account.forms import LoginForm
from account.decorators import admin_required
from sites.forms import FeedbackForm
from sites.models import Feedback 

import logging
import urllib
import sys
from books.models import Book, Author
import os
log = logging.getLogger("mysite")

def _downloadImg(url):
    '''下载书籍图片'''
    imgPath = settings.BOOKPIC_ROOT
    urlOpen = urllib.urlopen(url)
    imgDataRead = urlOpen.read(8192)
    imgDir = os.path.join(imgPath, os.path.basename(url))
    imgSave = open(imgDir, 'wb')
    while imgDataRead:
        imgSave.write(imgDataRead)
        imgDataRead = urlOpen.read(8192)
    imgSave.close()
    return "books/%s" % (os.path.basename(url))

def regBooks(request):
    '''利用豆瓣API获取书籍信息加入数据库'''
    DOUBAN = "https://api.douban.com/v2/book/search?q="
    q = request.REQUEST.get('q', '')
    q = urllib.quote(q.decode('utf8').encode('utf8'))  
    DOUBAN += q

    req = urllib.urlopen(DOUBAN)
    resp = req.read()
    result = simplejson.loads(resp)
    books = result['books']
    booksCount = len(books)
    for i in range(booksCount):
        author = Author()
        author.name = books[i]['author'][0]
        author.desc = books[i]['author_intro']
        author.save()
        
        book = Book()
        book.name = books[i]['title']
        book.author = author
        book.price = float(''.join([ item for item in books[i]['price'] if item in '1234567890.' ]))
        if not books[i]['isbn13']:
            book.isbn = books[i]['isbn10']
        else:
            book.isbn = books[i]['isbn13']
        book.press = books[i]['publisher']
        book.desc = books[i]['summary']
        book.binding = books[i]['binding']
        book.pages = books[i]['pages']
        book.img = _downloadImg(books[i]['image'])   
        book.stock = 140
        book.publish_date = books[i]['pubdate']
        book.save()
        
    return HttpResponse('success')

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
        RequestContext(request, 
                       {"feeds": Feedback.objects.getAllFeedbacks()}
                       )) 
    

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
