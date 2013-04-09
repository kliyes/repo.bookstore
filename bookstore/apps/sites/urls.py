'''
Created on 2013-4-7

@author: Tom
'''
from django.conf.urls.defaults import patterns, url
urlpatterns = patterns("",
    url(r"^reg_book/$", 'sites.views.regBooks'),
    url(r"^info/$", 'sites.views.info'),
    url(r"^add_book/$", 'sites.views.addBook'),
    url(r"^show_book/$", 'sites.views.bookShow'),
    url(r"^stat_book/$", 'sites.views.bookStat'),
    
)