#coding=utf-8
#
# Copyright (C) 2012-2013  XIZHI TECH Co., Ltd. All rights reserved.
#
# Created on 2013-3-18, by Administrator
#
# This file is part of lershare.com.
#
from books.models import Book, Cart, Order, BookComment, Grade
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
import json
import datetime

'''
File feature description here
'''
######
def getBooksByName(request):
    if request.method != "POST":
        return render_to_response('books/bookset.html', RequestContext(request))
    
    name = request.REQUEST.get('name', '')
    books = Book.objects.filter(name__icontains=name)
    
    return render_to_response('books/bookset.html', RequestContext(request, 
        {'books': books}))

def _getBookById(bookId):
    '''按书籍的id号查找书籍'''
    try:
        book = Book.objects.get(id=bookId)
    except Book.DoesNotExist:
        return False
    
    return book
   
   
def bookDetail(request, bookId):
    book = _getBookById(bookId)
    if not book:
        return HttpResponse(u'查无此书')
    
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    
    comments = book.getComments()
    grade = 1
    if request.user.is_authenticated():
        grade = book.getMarkedGrade(request.user.get_profile())
    
    return render_to_response('books/bookdetail.html', RequestContext(request, 
        {'book': book, 'comments': comments, 'grade': grade, 'cart': cart}))
    
@login_required
def addToCart(request, bookId):
    '''加入购物车, ajax request only'''
    if not request.is_ajax:
        raise Http404
    
    book = _getBookById(bookId)
    if not book:
        return HttpResponse(u'查无此书')
    
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    if not cart.addBook(book):
        return HttpResponse(json.dumps({'status': 'failed'}))
    
    return HttpResponse(json.dumps({'status': 'success'}))

def delFromCart(request, bookId):
    '''从购物车中移除书籍, ajax request only'''
    if not request.is_ajax:
        raise Http404
    
    book = _getBookById(bookId)
    if not book:
        return HttpResponse(u'查无此书')
    
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    if not cart.removeBook(book):
        return HttpResponse(json.dumps({'status': 'failed'}))
    
    t = get_template('books/includes/booklist.html')
    html = t.render(RequestContext(request, {'cart': cart}))
    
    return HttpResponse(json.dumps({'status': 'success', 'html': html}))

def checkCart(request):
    '''查看购物车'''
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    
    return render_to_response('books/bookcart.html', RequestContext(request, 
        {'cart': cart}))
    
def makeOrder(request):
    '''填写订单'''
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    
    if request.method != 'POST' or not cart.getBooks(): # 'POST'必须大写！ 
        return render_to_response('books/bookorder.html', RequestContext(request, 
            {'cart': cart}))
        
    addr = request.REQUEST.get('addr', None)
    contact = request.REQUEST.get('contact', None)
    makeDefault = request.REQUEST.get('default', None)
    if makeDefault == 'on':
        profile.addr = addr
        profile.contact = contact
        profile.save()
    order = Order()
    order.owner = profile
    order.total_fee = cart.getTotalFee()
    order.addr = addr
    order.contact = contact
    order.save()
    order.addBooks(cart.getBooks())
    # 提交订单后清空购物车中书籍
    profile.buyBooks(cart.getBooks())
    cart.removeBooks(cart.getBooks())
    
    return HttpResponse('Thanks!')
      
def addComment(request, bookId):
    '''添加书籍评论,ajax request only'''
    if not request.is_ajax():
        raise Http404
    
    cmtContent = request.REQUEST.get('cmtContent', '')
    profile = request.user.get_profile()
    book = _getBookById(bookId)
    cmt = BookComment(owner=profile, book=book, content=cmtContent)
    cmt.save()
    
    cmts = book.getComments()
    t = get_template('books/includes/commentlist.html')
    return HttpResponse(json.dumps({'status': 'success', 
        'html': t.render(RequestContext(request, {'comments': cmts}))}))

def markBook(request, bookId):
    '''为书籍打分,ajax request only'''
    if not request.is_ajax():
        raise Http404
    try:
        grade = request.REQUEST.get('grade', '')
        print grade
        profile = request.user.get_profile()
        book = _getBookById(bookId)
        bookGrade = Grade(marker=profile, book=book, value=int(grade))
        bookGrade.save()
    except Exception, e:
        print e
        return HttpResponse(json.dumps({'status': 'failed'}))
    
    return HttpResponse(json.dumps({'status': 'success'}))




    
