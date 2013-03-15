#coding=utf-8
import traceback, uuid, datetime

from django.contrib import messages
from django.http import HttpResponse

from django.utils import simplejson as json 

# 用于求字符串长度，中文汉字计为两个英文字母长度
ecode = lambda s: s.encode('gb18030')


##################################################
#  date and time processing utils
##################################################
def today():
    return datetime.date.today()

def yesterday():
    return today() + datetime.timedelta(days=-1)

def tomorrow():
    return today() + datetime.timedelta(days=1)

def weekday():
    '''获取今天星期几， 如，1对应星期一，4对应周期四，6对应周六等'''
    return datetime.date.isoweekday(datetime.date.today())

def monday():
    '''获取当前周星期一的日期'''
    d = today()
    delta = datetime.date.isoweekday(d) - 1
    return d - datetime.timedelta(days=delta)

def saturday():
    '''获取当前周周六的日期'''
    d = today()
    delta = 7 - datetime.date.isoweekday(d)
    return d + datetime.timedelta(days=delta-1)       

def sunday():
    '''获取当前周周日的日期'''
    d = today()
    delta = 7 - datetime.date.isoweekday(d)
    return d + datetime.timedelta(days=delta)


'''######################################
    
'''


def genUuid():
    return str(uuid.uuid1())

def toJson(dict):
    """convert python dict object to json format, like ... """
    return json.dumps(dict)

def jsonResponse(dict):
    return HttpResponse(toJson(dict))

def log(msg):
    """ replace this with the real log way later, not "print"  """
    print msg

def replaceHttp(website):
    (website.replace("http://", ""))
    return 

def save2session(request, key, value):
    request.session[key] = value
    
def clear2session(request, key):
    request.session[key] = None
    
def getFromSession(request, key):
    return request.session[key]         

def addQueryParam(url, paramKey, paramValue):
    '''append a query param for a url'''
    if hasQuestionMark(url):
        return "%s&%s=%s" % (url, paramKey, paramValue)
    else:
        return "%s?%s=%s" % (url, paramKey, paramValue)

def hasQuestionMark(urlStr):
    """查找URL字符串，是否有?号"""
    index = urlStr.find("?")
    if index == -1:
        return False

    return True 

def addMsg(request, msgCode, msg):
    messages.add_message(request, msgCode, msg)

def log_error(func):
    """异常装饰器"""
    def _call_func(*args, **argd):
        try:
            return func(*args, **argd)
        except:
            import logging
            log = logging.getLogger("mysite")
            log.debug(traceBack()) 
    return _call_func

def traceBack():  
    """ print exception stack """
    try:  
        return traceback.print_exc()  
    except:  
        return '' 

def sort(list, sortedBy, reversed=True):
    """
    将列表中数据排序
    list: 目标列表. 
    sortedBy: 排序关键字
    reversed: True-反向 False-正向  
    """
    return sorted(list, key=lambda item: sortedBy, reverse=reversed)   
    
    
    