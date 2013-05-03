#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.conf import settings

# 默认跳转页
DEFAULT_PAGE = 1 
# 分页GET请求参数名
PAGE_KEY = "page"

EMPTY_PAGE_DATA = {'pageItems': None, 'pageRange': None}

## try this to return only one paging object, TODO...
def pagingAjaxData(request, dataKey, currentPageNo):
    """ 
    处理ajax分页请求,返回每页数据集pageItems以及页数范围pageRange.
    
    params:
        request:        请求对象，从中获取session
        dataKey:        通过该key值，从session中获取paging分页对象
        currentPageNo:  当前页号
    
    return:
        {pageItems, pageRange}: 字典对象, 根据不同页面的需求在各views中进行渲染
    """
    paging = getSessionPaging(request, dataKey)
    if not paging:
        return None
    
    return paging.result(currentPageNo)

def getRequestPageNo(request):
    """ 从request对象中获取所请求的页号参数名,以page命名. 默认页号为1 """
    return int(request.REQUEST.get(PAGE_KEY, DEFAULT_PAGE))

def setSessionPaging(request, dataKey, dataList, pageSize=10):
    """将数据存入session,用于后续分页请求"""
    request.session[dataKey] = Paging(dataList, pageSize)
    return request.session[dataKey]
   
def getSessionPaging(request, pagingKey):
    """ Get data paging object from session by key passed """
    return request.session.get(pagingKey, None)    

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
        except(InvalidPage):
            return self.paginator.page(self.paginator.num_pages)
    
    def pageRange(self, requestPageNo):
        """ 得到分页范围 """
        
        pageNo = _validatePageNo(requestPageNo)
        if pageNo >= settings.AFTER_RANGE_NUM:
            return self.paginator.page_range[
                pageNo - settings.AFTER_RANGE_NUM : 
                pageNo + settings.BEFORE_RANGE_NUM]
        return self.paginator.page_range[0: pageNo + settings.BEFORE_RANGE_NUM] 
        
    def result(self, pageNo, pageItemsKey="pageItems", pageRangeKey="pageRange"):
        #返回指定页面的结果数据
        
        return {
            pageItemsKey: self.currentPageData(pageNo), 
            pageRangeKey: self.pageRange(pageNo)
        }
    
    # ##################################following todo...
    '''
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
    '''
    
    