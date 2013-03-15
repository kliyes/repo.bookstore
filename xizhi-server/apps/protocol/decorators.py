#coding=utf8

# ensure_csrf_cookie only in django1.4.2
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from common.utils import jsonResponse
from protocol.models import Client
from api import errors
from api import consts
from django.http import Http404

def post_request_required(func):
    """装饰器: 用于过滤POST请求"""

    def passPostRequest(request, *args, **kwargs):
        if request.method == "POST":
            return func(request, *args, **kwargs)
        return jsonResponse(errors.NOT_POST_REQUEST)        
    return passPostRequest

def get_request_required(func):
    """装饰器: 过滤get请求"""

    def passGetRequest(request, *args, **kwargs):
        if request.method == "GET":
            return func(request, *args, **kwargs)
        return jsonResponse({"status": "Not GET request"})        
    return passGetRequest

@csrf_exempt
def authorized(func):
    """验证客户端请求合法性
        when authorizing the clients to access server APIs, 
        the @csrf_exempt is needed,
        use cache to store the authorized clien key later TODO... 
    """
    
    def _authorized(request, *args, **kwargs):
        clientKey = getClientKeyFromRequest(request)
        if not clientKey:
            return jsonResponse(errors.CLIENT_AUTHORIZED_ERR)
        
        try:
            client = Client.objects.getByKey(clientKey)
        except Client.DoesNotExist:
            return jsonResponse(errors.CLIENT_KEY_ERR)

        return func(request, *args, **kwargs)
    return _authorized

def getClientKeyFromRequest(request):
    """Get client key from cookie, or from request params"""
    clientKey = request.COOKIES.get(consts.CLIENT_KEY, None)
    if clientKey is None:
        clientKey = request.REQUEST.get(consts.CLIENT_KEY, None)
    
    return clientKey

    
    
    
