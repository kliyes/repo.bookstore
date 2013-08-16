#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns("",
    url(r"^getbyname/$", "books.views.getBooksByName", name="book_search"),
    url(r"^getbycate/(\w+)$", "books.views.getBooksByCate", name="book_get_by_cate"),
    url(r"^(\d+)$", "books.views.bookDetail", name="book_detail"), 
    url(r"^add_to_cart/(\d+)$", "books.views.addToCart", name="book_cart_add"), 
    url(r"^del_from_cart/(\d+)$", "books.views.delFromCart", name="book_cart_del"), 
    url(r"^check_the_cart/$", "books.views.checkCart", name="book_cart_check"), 
    url(r"^make_order/$", "books.views.makeOrder", name="book_order"), 
    url(r"^submit_order/$", "books.views.submitOrder", name="book_order_submit"), 
    
    url(r"^comment/(\d+)$", "books.views.goComment", name="book_comment"), 
    
    url(r"^add_comment/(\d+)$", "books.views.addComment", name="book_add_cmt"), 
    url(r"^page_books/(\w+)/$", "books.views.pagingBooks"), 
    url(r"^page_all_books/$", "books.views.pagingAll"), 
    url(r"^page_cmts/(\d+)$", "books.views.pagingCmts"), 

    url(r"^page_book_cmts/(\d+)$", "books.views.pagingBookCmts", name="book_page_cmts"), 
    
    url(r"^comment_done/$", 'books.views.commentDone', name="comment_done"),
    url(r"^thanks/$", TemplateView.as_view(template_name="books/success_bought.html"), name="thanks"), 
    url(r"^test/$", "books.views.test_serializer"),
)
