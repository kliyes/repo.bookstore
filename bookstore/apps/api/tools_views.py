'''
Created on Nov 2, 2012

@author: junn
'''

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from account.decorators import admin_required

@admin_required
def testConsole(request):
    return render_to_response("tools/lvy_api_tester.html", RequestContext(request))