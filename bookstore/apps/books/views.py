'''
Created on 2013-3-14

@author: Tom
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def test(request):
    return render_to_response('books/test.html', RequestContext(request, 
                                                     {'word':'!!!!!'}))