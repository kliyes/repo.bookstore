'''
Created on 2013-7-7

@author: Tom
'''
from django.conf.urls.defaults import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from books import api_views

urlpatterns = patterns('',
    url(r'^$', api_views.BookList.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', api_views.BookDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)