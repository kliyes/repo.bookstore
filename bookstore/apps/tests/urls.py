#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^$",          "tests.views.test", name="test"), 
    url(r"^html/$",     direct_to_template, {"template": settings.TEMPLATE_TEST}), # 用于测试新的HTML页面 
    url(r"^logout/$",   "tests.views.myLogout", name="my_logout"),
    url(r"^user/$",     "tests.views.getUserinfo"),
    url(r"^clear_cache/$",      "tests.views.clearCache"),
)
