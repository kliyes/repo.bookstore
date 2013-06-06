#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import logging

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from idios.models import ProfileBase

from books.models import BookComment, Cart, Order

logger = logging.getLogger("mysite")
NOTICE_UNREAD = 0
NOTICE_READ = 1

CITY_KEY_PREFIX = 'city_'
AREA_KEY_PREFIX = 'area_'
TAG_KEY_PREFIX  = 'tag_'

        

class ProfileManager(models.Manager):
    def totalUsers(self):
        return Profile.objects.all().count()
    
class Profile(ProfileBase):
    delOrderIds = [] # 用户删除（屏蔽）的订单id列表
    
    name = models.CharField(_("name"), max_length=50, default='', null=True, blank=True)        #昵称
    desc = models.TextField(_("about"), max_length=200, default='', null=True, blank=True)      #个人介绍
    sex = models.CharField(_("sex"), default="unknown", max_length=20, null=True, blank=True)   #性别
    
    # user's pic
    big_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC)                                  
    normal_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC_NORMAL)                          
    small_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC_SMALL)  
    
    # 为临时保存用户上传的头像图片,添加该字段
    tmp_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC, null=True, blank=True)          #临时头像文件
    
    is_authed = models.BooleanField()                               #是否认证用户, 0-未认证 1-已认证
    is_organ = models.BooleanField()                                #是否是机构,0-个人 1-机构
    login_count = models.IntegerField(default=0)                    #登录次数
    
    #===============================================
    #code in bookstore
    receiver = models.CharField(max_length=30, null=True, blank=True) # 收货人
    contact = models.CharField(max_length=20) # 联系方式（手机号码）
    addr = models.CharField(max_length=200) # 送货地址
    
    #===============================================
    #code in bookstore
    bought_books = models.ManyToManyField(
        "books.Book", related_name="boughtBooks",  
        verbose_name=u"用户买过的书籍列表", 
        db_table='t_bought_books'
    )
    #===============================================
    
    objects = ProfileManager()

    class Meta:
        db_table = 't_profile'
        verbose_name = 'Profile'
    
    def __unicode__(self):
        if self.name is None:
            return "id:", self.id
        return u"id:%s name:%s" % (self.id, self.name)

    # ---------------------------business methods -------------------------    
    def updateLoginCount(self):
        """登录次数加1"""
        self.login_count += 1
        self.save() 
    
    #===============================================
    #code in bookstore
    def buyBooks(self, books):
        '''购买图书'''
        for book in books:
            self.bought_books.add(book)
            book.bought_count += 1
            book.save()
        return True
    
    def getBoughtBooks(self):
        '''获取所购买书籍'''
        return self.bought_books.all()
    
    def getOwnedComments(self):
        '''获取该用户发表的评论'''
        return BookComment.objects.filter(owner=self)
    
    def getOrders(self):
        '''获取该用户所有订单'''
        return Order.objects.filter(owner=self)
    
    def getCartItemsCount(self):
        '''获得该用户购物车项目总数'''
        cart = Cart.objects.get(owner=self)
        return cart.getItemsCount()
    
    def getCartBooks(self):
        '''获得该用户购物车中的书籍'''
        cart = Cart.objects.get(owner=self)
        return cart.getBooks()
    #===============================================
    
    def getAgreedComments(self):
        return self.agreed_comments.all()
            
    def agreeComment(self, cmt):
        try:
            self.agreed_comments.add(cmt)
            cmt.agree_count += 1
            cmt.save()
            return True
        except:
            logger.warning("Profile %s agree comment %s exception"% (self.id, cmt.id))
            return False
                 

    
    
