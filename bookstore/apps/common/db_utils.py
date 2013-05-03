#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.db import connection

def sql(querySet):
    '''获取查询SQL'''
    return querySet.query
    
    
    