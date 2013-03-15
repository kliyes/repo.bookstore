#coding=utf8

'''
Created on Oct 25, 2012

@author: junn
'''

from hashlib import sha512
from uuid import uuid4

from django.db import models
from django.conf import settings


CLIENT_KEY_LENGTH = 30
CLIENT_SECRET_LENGTH = 30

import logging
logger = logging.getLogger("mysite")

class KeyGenerator(object):
    """Callable Key Generator that returns a random keystring.

    **Args:**

    * *length:* A integer indicating how long the key should be.

    *Returns str*
    """
    def __init__(self, length):
        self.length = length

    def __call__(self):
        return sha512(uuid4().hex).hexdigest()[0:self.length]

CLIENT_KEY_PREFIX = 'client_'
class ClientManager(models.Manager):
    def getByKey(self, key):
        if not settings.CACHED_CLIENTS:
            initGlobalClientData()
        return settings.CACHED_CLIENTS.get("%s%s" % (CLIENT_KEY_PREFIX, key), None)    

class Client(models.Model):
    name = models.CharField(max_length=256)
    key = models.CharField(
        unique=True,
        max_length=CLIENT_KEY_LENGTH,
        default=KeyGenerator(CLIENT_KEY_LENGTH),
        db_index=True)
    
    password = models.CharField(
        unique=True,
        max_length=CLIENT_SECRET_LENGTH,
        default=KeyGenerator(CLIENT_SECRET_LENGTH))

    desc = models.TextField(null=True, blank=True)
    
    objects = ClientManager()
    
def initGlobalClientData():    
    clients = Client.objects.all()
    for client in clients:
        settings.CACHED_CLIENTS["%s%s" % (CLIENT_KEY_PREFIX, client.key)] = client  
    logger.info("====> Global Client authorizing data initialized")

#initGlobalClientData()    
    