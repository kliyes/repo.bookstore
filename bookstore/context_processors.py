#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.conf import settings

"""
    载入常量设置
"""

def importSettings(request):
    return {
        #picture size
        "P_BIG_W": settings.PIC_SIZE_BIG[0],
        "P_BIG_H": settings.PIC_SIZE_BIG[1],
        "P_NORMAL_W": settings.PIC_SIZE_NORMAL[0],
        "P_NORMAL_H": settings.PIC_SIZE_NORMAL[1],
        "P_SMALL_W": settings.PIC_SIZE_SMALL[0],
        "P_SMALL_H": settings.PIC_SIZE_SMALL[1],
        
        #poster size
        "POS_BIG_W":    settings.POSTER_SIZE_BIG[0],
        "POS_BIG_H":    settings.POSTER_SIZE_BIG[1],
        "POS_NORMAL_W": settings.POSTER_SIZE_NORMAL[0],
        "POS_NORMAL_H": settings.POSTER_SIZE_NORMAL[1],
        "POS_SMALL_W":  settings.POSTER_SIZE_SMALL[0],
        "POS_SMALL_H":  settings.POSTER_SIZE_SMALL[1],
    }
