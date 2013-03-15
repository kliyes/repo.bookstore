'''
Created on Oct 22, 2012

@author: junn
'''

import random

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib import messages

from protocol.models import Client
from protocol.decorators import authorized
from account.decorators import admin_required
from common import utils


@admin_required
def requestClientKey(request):
    clients = Client.objects.all()[:50]
    if clients is None or len(clients) == 0:
        client = Client(name="default")
        client.save()
        return utils.jsonResponse({"client_key": client.key})
    return utils.jsonResponse({"client_key": clients[random.randrange(0,len(clients))].key})

@admin_required
def createClient(request):
    if request.method != 'POST':
        clients = Client.objects.all()
        return render_to_response("protocol/clients.html", RequestContext(request, 
            {"clients":clients}))

    clientName = request.POST.get("clientName", '')
    client = Client(name=clientName)
    client.save()
    return HttpResponseRedirect("/protocol/create_client/")

@admin_required
def removeClient(request, clientId):
    try:
        client = Client.objects.get(id=clientId)
        client.delete()
        utils.addMsg(request, messages.INFO, "Client (%s, %s) deleted successfully" % 
                     (client.id, client.name))
        return HttpResponseRedirect("/protocol/create_client/")
    except Client.DoesNotExist:
        raise Http404
        
        
        
        
        
        