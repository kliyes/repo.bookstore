#coding=utf-8
#
# Copyright (C) 2012-2013 XIZHI TECH Co., Ltd. All rights reserved.
# Created on 2013-8-1, by Tom
#
#
from django.conf.urls import patterns, url
from account import api_views


urlpatterns = patterns("",
    url(r"^login/$",api_views.Login.as_view()),
    
)