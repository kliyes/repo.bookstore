#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

from profiles.views import * 


urlpatterns = patterns("",
    url(r"^setting/$", "profiles.views.setProfile", name="profiles_setting"),
    url(r"^change_city/(\d+)/$", "profiles.views.changeCity", name="profiles_change_city"),
    url(r"^init_pic/$", "profiles.views.initPic", {"template": "profiles/set_picture.html",}, name="profiles_initpic"),
    url(r"^cancel_pic_setup/$", "profiles.views.cancelPicSetup", name="profiles_cancel_picsetup"),
    url(r"^set_pic/$", "profiles.views.setPic", {"template": "profiles/set_picture.html",}, name="profiles_setpic"),
    url(r"^add_tag/$", "profiles.views.addTag", name="profiles_addtag"),
    url(r"^remove_tag/$", "profiles.views.removeTag", name="profiles_removetag"),
    
    url(r"^save_profile/$", "profiles.views.save_profile", name="profiles_save"), 
    
    url(r"^check_orders/$", "profiles.views.checkOrders", name="profiles_order_check"),
    url(r"^page_orders/$", "profiles.views.pagingOrders", name="profiles_order_page"),
    url(r"^order_del_by_profile/$", "profiles.views.delOrderByProfile", name="profiles_order_del_by_profile"),

)
