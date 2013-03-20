#coding=utf-8
#
# Copyright (C) 2012-2013  XIZHI TECH Co., Ltd. All rights reserved.
#
# Created on 2013-3-18, by Administrator
#
# This file is part of lershare.com.
#
from books.models import Book
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse

'''
File feature description here
'''
def getBooksByName(request):
    name = request.REQUEST.get('name', '')
    books = Book.objects.filter(name__icontains=name)
    
    return render_to_response('books/bookset.html', RequestContext(request, 
        {'books': books}))
    
def bookDetail(request, bookId):
    if not bookId:
        return
    try:
        book = Book.objects.get(id=bookId)
    except Book.DoesNotExist:
        return HttpResponse(u'查无此书')
    
    comments = book.getComments()
    
    return render_to_response('books/bookdetail.html', RequestContext(request, 
        {'book': book, 'comments': comments}))

