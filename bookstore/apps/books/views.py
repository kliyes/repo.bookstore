#coding=utf-8
#
# Copyright (C) 2012-2013  XIZHI TECH Co., Ltd. All rights reserved.
#
# Created on 2013-3-18, by Administrator
#
# This file is part of lershare.com.
#
from books.models import Book, Cart
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
    
    comments = book.getComments()
    
    return render_to_response('books/bookdetail.html', RequestContext(request, 
        {'book': book, 'comments': comments}))

def addToCart(request, bookId):
    '''加入购物车'''
    book = _getBookById(bookId)
    if not book:
        return HttpResponse(u'查无此书')
    
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    if not cart.addBook(book):
        return HttpResponse(u'操作失败')
    
    return render_to_response('books/booklist.html', RequestContext(request, 
        {'book': book}))
    
def checkCart(request):
    '''查看购物车'''
    profile = request.user.get_profile()
    cart = Cart.objects.get(owner=profile)
    bookList = cart.getBooks()
    
    return render_to_response('books/bookcart.html', RequestContext(request, 
        {'booklist': bookList}))
    
    
    
    
    
    
