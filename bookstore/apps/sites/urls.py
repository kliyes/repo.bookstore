#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

from books.models import Category

urlpatterns = patterns("",
    url(r"^$", 'sites.views.adminHome', name='management'), 
    url(r"^reg_book/$", 'sites.views.regBooks', name='regBook'),
    url(r"^add_book/$", 'sites.views.addBook', name='addBook'),
    url(r"^show_book/$", 'sites.views.bookShow', name='showBook'),
#    url(r"^stat_book/$", TemplateView.as_view(temelate_name="sites/stat.html", extra_context={'cates': Category.objects.all()}}, name='statBook'),
    url(r"^update_orders/$", 'sites.views.updateOrders', name='updateOrders'),
    
)