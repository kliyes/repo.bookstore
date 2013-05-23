#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
from django.conf.urls.static import static
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

handler500 = "pinax.views.server_error"
####
urlpatterns = patterns("",
                       
    #url(r"", direct_to_template, {"template": "index.html",}, name="index"), #工程下所有链接都将被重置到index.html页面
    url(r"^$", "books.views.goHome", name="welcome"),

    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", 
        name="admin_invite_user"),
    #url(r"^admin/", include(admin.site.urls)),    

    #url(r"^home/$", {"template": "index.html",}, name="home"),
    url(r"^account/", include("account.urls")),
    url(r"^admin/login/$", "account.views.adminLogin", name="admin_login"),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^books/", include("books.urls")),
    
    ## use this to test html page
    url(r"^test/", include("tests.urls")),
    
     # site navigation
    url(r"^us/555/$", 'sites.views.siteAnnouncement', name="us_555"),
#    url(r"^us/about/$", direct_to_template, {"template": "site/about.html"}, name="us_about"),
#    url(r"^us/contact/$", direct_to_template, {"template": "site/contact.html"}, name="us_contact"),
#    url(r"^us/join/$", direct_to_template, {"template": "site/job.html"}, name="us_job"),
    url(r"^us/feedback/$", "sites.views.submitFeedback", name="us_feedback"),
#    url(r"^us/feedback/view$", "sites.views.viewFeedbacks", name="us_feedback_view"),
#    url(r"^us/onlines/$", "sites.views.getOnlines", name="online_info"),
    url(r"^addbooks/$", "sites.views.regFromDouban"),
    url(r"^manage/", include("sites.urls")),
    
#    url(r"^notices/", include("notification.urls")),
    
)

urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT )
