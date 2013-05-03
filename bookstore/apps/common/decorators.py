#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import logging
from hashlib import sha1

try:
    from cPickle import dumps
except:
    from cPickle import dumps

from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger("mysite")

def make_key(fn, args, kwargs):
    '''根据函数名及参数生成cache key'''
    cache_indentifiers = "%s%s%s%s" % (
         fn.__module__, fn.__name__, dumps(args), dumps(kwargs)
    )
    return sha1(cache_indentifiers).hexdigest()    

cache_miss = object()
def cache_data(timeout=settings.DEFAULT_CACHE_TIME_OUT):
    '''装饰器:
        缓存函数执行结果, 以[函数名+参数]为key
        timeout: 缓存的时间,单位秒.默认设置为10min
    '''
    def wrapper(fn):
        def decorator(*args, **kwargs):
            cache_key = make_key(fn, args, kwargs)  #is this error?
            value = cache.get(cache_key, cache_miss)
            if value is cache_miss:
                value = fn(*args, **kwargs)
                cache.set(cache_key, value, timeout)
                logger.debug("Cached data: [key-%s, timeout-%s]" % (cache_key, timeout))
            else:
                logger.debug("Get data from cache: [key-%s, timeout-%s]" % (cache_key, timeout))    
            return value
        return decorator
    return wrapper
