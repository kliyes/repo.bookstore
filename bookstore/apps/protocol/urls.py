#-*- coding: utf-8 -*-
'''
Created on Oct 22, 2012

@author: junn
'''

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^create_client/$',   'protocol.views.createClient', name="protocol_create_client"),
    url(r'^remove_client/(\d+)$',   'protocol.views.removeClient', name="protocol_remove_client"),
    url(r'^request_client_key/$',   'protocol.views.requestClientKey', name="protocol_request_key"),
)