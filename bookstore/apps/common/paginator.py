#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.template.loader import get_template
from django.template import RequestContext
from django.conf import settings

# 默认跳转页
DEFAULT_PAGE = 1 
# 分页GET请求参数名
PAGE_KEY = "page"
 

## try this to return only one paging object, TODO...
def pagingData(request, dataKey, currentPageNo, destListKey, destTemplate):
    """ 
    处理ajax分页请求,返回渲染新页数据后的HTML页面片断.
    
    request:        请求对象，从中获取session
    dataKey:        通过该key值，从session中获取paging分页对象
    currentPageNo:  当前页号
    destListKey:    处理后的结果数据列表, render到目标模板页面的变量名
    destTemplate:   render的目标模板页面
    
    return:
        html页面片断, 用法: HttpResponse(json.dumps({"html": html}))
    """
    paging = getPaing(request, dataKey)
    if not paging:
        return None
    
    try:
        t = get_template(destTemplate)
        return t.render(RequestContext(request, {
           destListKey: paging.currentPageData(currentPageNo),
           "pageRange": paging.pageRange(currentPageNo),
        }))
    except:
        return None
 
def getRequestPageNo(request):
    """ 从request对象中获取所请求的页号参数名,以page命名. 默认页号为1 """
    return int(request.GET.get(PAGE_KEY, DEFAULT_PAGE))

def setSessionPaging(request, dataKey, dataList, pageSize=10):
    """将数据存入session,以备后续分页请求"""
    request.session[dataKey] = None
    request.session[dataKey] = Paging(dataList, pageSize)    
    return Paging(dataList, pageSize)   
   
def getPaing(request, dataKey):
    """ Get data paging object from session by key passed """
    return request.session.get(dataKey, None)    

def _validatePageNo(page):
    """验证页号是否小于1，或者页号输入错误。默认跳转到第1页"""

    try:
        page = int(page)
        if page < DEFAULT_PAGE:
            return DEFAULT_PAGE
    except ValueError:
        return DEFAULT_PAGE
    return page    
    
class Paging(object):
    """ 用于分页处理. 构造：paging = Paging(objectList)，其中 
    object_list: 目标分页对象
    page_size:  每页items数量
    """
    
    paginator = None
     
    def __init__(self, object_list, page_size):
        self.paginator = Paginator(object_list, page_size)
    
    def currentPageData(self, requestPageNo):
        """ 传入页号，获取页面所对应的数据列表 """
        
        pageNo = _validatePageNo(requestPageNo)
        try:
            return self.paginator.page(pageNo)
        except(EmptyPage, InvalidPage, PageNotAnInteger):
            return self.paginator.page(self.paginator.num_pages)
    
    def pageRange(self, requestPageNo):
        """ 得到分页范围 """
        
        pageNo = _validatePageNo(requestPageNo)
        if pageNo >= settings.AFTER_RANGE_NUM:
            return self.paginator.page_range[
                pageNo - settings.AFTER_RANGE_NUM : 
                pageNo + settings.BEFORE_RANGE_NUM]
        return self.paginator.page_range[0: pageNo + settings.BEFORE_RANGE_NUM]
    
    # ##################################following todo...
    def total_pages(self):
        return self.paginator.num_pages
    
    def has_previous(self):
        pass
    
    def has_next(self):
        pass
    
    def page_range(self):
        #return self.pageRange(requestPageNo)
        pass
    
    def current_page_number(self):
        pass
    
    def previous_page_number(self):
        pass
    
    def next_page_number(self):
        pass

    
    