'''
Created on 2013-4-7

@author: Tom
'''
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from books.models import Category
urlpatterns = patterns("",
    url(r"^reg_book/$", 'sites.views.regBooks'),
    url(r"^add_book/$", 'sites.views.addBook'),
    url(r"^show_book/$", 'sites.views.bookShow'),
    url(r"^stat_book/$", direct_to_template, {"template": "sites/stat.html", 
        'extra_context': {'cates': Category.objects.all()}}),
    url(r"^update_orders/$", 'sites.views.updateOrders'),
    
)