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

def _downloadImg(url, size="medium"):
    '''下载书籍图片 size: 图片尺寸'''
    if size == "small":
        imgPath = settings.SBPIC_ROOT
    elif size == "medium":
        imgPath = settings.MBPIC_ROOT
    else:
        imgPath = settings.LBPIC_ROOT
    urlOpen = urllib.urlopen(url)
    imgDataRead = urlOpen.read(8192)
    imgDir = os.path.join(imgPath, os.path.basename(url))
    imgSave = open(imgDir, 'wb')
    while imgDataRead:
        imgSave.write(imgDataRead)
        imgDataRead = urlOpen.read(8192)
    imgSave.close()
    return "books/%s/%s" % (size, os.path.basename(url))

def regFromDouban(request):
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
        book.spic = _downloadImg(books[i]['images']['small'], 'small')   
        book.mpic = _downloadImg(books[i]['images']['medium'], 'medium')   
        book.lpic = _downloadImg(books[i]['images']['large'], 'large')   
        book.stock = 140
        book.publish_date = books[i]['pubdate']
        book.save()
        
    return HttpResponse('success')


def regBooks(request):
    '''调用豆瓣API,根据图书isbn号获取图书信息'''
    URL = 'https://api.douban.com/v2/book/isbn/'
    if request.method != "POST":
        return render_to_response('books/regbook.html', RequestContext(request))
    
    isbn = request.REQUEST.get('isbn', '')
    if isbn != '':
        req = urllib.urlopen(URL+str(isbn))
        resp = req.read()
        result = simplejson.loads(resp)
        #author = Author()
        author_name = result['author'][0]
        author_desc = result['author_intro']
        #author.save()
        
        #ook = Book()
        book_name = result['title']
        #book.author = author
        book_price = result['price']
        if not result['isbn13']:
            book_isbn = result['isbn10']
        else:
            book_isbn = result['isbn13']
        book_press = result['publisher']
        book_desc = result['summary']
        book_binding = result['binding']
        book_pages = result['pages']
        book_spic = _downloadImg(result['images']['small'], 'small')   
        book_mpic = _downloadImg(result['images']['medium'], 'medium')   
        book_lpic = _downloadImg(result['images']['large'], 'large')   
        #book_stock = 140
        book_publish_date = result['pubdate']
        #book.save()
        
    ctx = {'authorName': author_name, 
           'authorDesc': author_desc, 
           'bookName': book_name, 
           'bookPrice': book_price, 
           'bookIsbn': book_isbn, 
           'bookPress': book_press, 
           'bookDesc': book_desc, 
           'bookBinding': book_binding, 
           'bookPages': book_pages, 
           'bookSpic': book_spic, 
           'bookMpic': book_mpic, 
           'bookLpic': book_lpic, 
           'bookPublishDate': book_publish_date}
    return render_to_response('books/regbook.html', RequestContext(request, ctx))
    
def addBook(request):
    if request.method != "POST":
        raise Http404
    
    authorName = request.REQUEST.get('authorName', None)
    authorDesc = request.REQUEST.get('authorDesc', None)
    bookName = request.REQUEST.get('bookName', None)
    bookPrice = request.REQUEST.get('bookPrice', None)
    bookIsbn = request.REQUEST.get('bookIsbn', None)
    bookPress = request.REQUEST.get('bookPress', None)
    bookDesc = request.REQUEST.get('bookDesc', None)
    bookBinding = request.REQUEST.get('bookBinding', None)
    bookPages = request.REQUEST.get('bookPages', None)
    bookSpic = request.REQUEST.get('bookSpic', None)
    bookMpic = request.REQUEST.get('bookMpic', None)
    bookLpic = request.REQUEST.get('bookLpic', None)
    bookPublishDate = request.REQUEST.get('bookPublishDate', None)
    stock = request.REQUEST.get('stock', None)
    #category = request.REQUEST.get('category', None)
    
    author = Author(name=authorName, desc=authorDesc)
    author.save()
    
    price = float(''.join([ item for item in bookPrice if item in '1234567890.' ]))
    book = Book(name=bookName, author=author, price=price, isbn=bookIsbn, 
                press=bookPress, desc=bookDesc, binding=bookBinding, 
                pages=bookPages, spic=bookSpic, mpic=bookMpic, lpic=bookLpic, 
                publish_date=bookPublishDate, stock=stock)
    book.save()
    return HttpResponseRedirect('/manage/reg_book/')

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
