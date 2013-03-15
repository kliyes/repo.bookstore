#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns("",
                       
    ## account APIs
    url(r"^account/login/$",    "api.account_views.login",          name="api_acct_login"),
    url(r"^account/signup/$",    "api.account_views.signup",          name="api_acct_signup"),
    url(r"^account/logout/$",    "api.account_views.logout",          name="api_acct_logout"),
    
    ## profile APIs
    url(r"^profiles/update/$",  "api.profile_views.updateProfile",  name="api_update_profile"),
    
    ## activity APIs
    url(r"^activity/$",         "api.activity_views.detailActivity", name="api_detail_activity"), #活动详情
    url(r"^activity/join/$",    "api.activity_views.joinActivity", name="api_join_activity"),
    
    ## APIs testing tools, by lvy
    #url(r"^tools/$",        direct_to_template, {"template": "tools/api_tester.html"}, name="api_tools"),
    url(r"^tools/$", "api.tools_views.testConsole", name="api_tools"),
    
)