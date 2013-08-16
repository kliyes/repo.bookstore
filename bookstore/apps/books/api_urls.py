#coding=utf-8
'''
Created on 2013-7-7

@author: Tom
'''
from django.conf.urls.defaults import *
from rest_framework.urlpatterns import format_suffix_patterns
from books import api_views

urlpatterns = patterns('',
    url(r'^$', api_views.BookList.as_view()),
    url(r'^get/$', api_views.BookDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)