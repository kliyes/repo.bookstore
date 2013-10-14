#coding=utf-8
#
# Copyright (C) 2012-2013 XIZHI TECH Co., Ltd. All rights reserved.
# Created on 2013-8-1, by Tom
#
#
from account import api_views
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"^login/$",api_views.Login.as_view()),
    url(r"^get_user_info/$",api_views.GetUserInfo.as_view()),
    
)