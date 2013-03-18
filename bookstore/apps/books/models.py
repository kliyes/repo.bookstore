#coding=utf-8
#
# Copyright (C) 2012-2013  XIZHI TECH Co., Ltd. All rights reserved.
#
# Created on 2013-3-18, by Administrator
#
# This file is part of lershare.com.
#
import datetime

from django.db import models

'''
File feature description here
'''
class Author(models.Model):
    '''定义Author模型'''
    name = models.CharField(max_length=40) # 姓名
    desc = models.CharField(max_length=8000) # 简介
    work_count = models.IntegerField() # 作品数量
    
    class Meta:
        db_table = 't_author'
        verbose_name = 'Author'
        app_label = 'books'
        
    def __unicode__(self):
        return u"id:%s name:%s" % (self.id, self.name)


class Category(models.Model):
    '''定义书籍分类模型'''
    name = models.CharField(max_length=20) # 名称
    count = models.IntegerField() # 该分类下的书籍数量
    
    class Meta:
        db_table = 't_category'
        verbose_name = 'Category'
        app_label = 'books'
        
    def __unicode__(self):
        return u"id:%s name:%s" % (self.id, self.name)
    

class BookManager(models.Manager):
    def totalBooks(self):
        return Book.objects.all().count()

class Book(models.Model):
    '''定义Book模型'''
    name = models.CharField(max_length=100) # 书名
    author = models.ForeignKey(Author) # 作者
    price = models.FloatField() # 定价
    isbn = models.CharField(max_length=20) # ISBN号
    press = models.CharField(max_length=200) # 出版社
    desc = models.CharField(max_length=8000) # 简介
    binding = models.CharField(max_length=10) # 装潢类型
    pages = models.CharField(max_length=9999) # 页数 
    img = models.CharField(max_length=80) # 图片
    bought_count = models.IntegerField() # 被购次数
    category = models.ForeignKey(Category) # 类别
    stock = models.IntegerField() # 库存
    publish_date = models.DateTimeField() # 出版日期
    reg_date = models.DateTimeField(default=datetime.datetime.now()) # 上架时间
    
    objects = BookManager()
    
    class Meta:
        db_table = 't_book'
        verbose_name = 'Book'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s name:%s" % (self.id, self.name)
    
    def getComments(self):
        '''获得该书的所有评论'''
        return Comment.objects.filter(book=self).order_by('-created_date')
    

class Comment(models.Model):
    '''定义评论模型'''
    owner = models.ForeignKey('profiles.Profile', related_name="commenter") # 评论发表者
    book = models.ForeignKey(Book) # 所评论的书籍
    content = models.CharField(max_length=1000) # 评论内容
    created_date = models.DateTimeField(default=datetime.datetime.now()) # 评论时间
    
    class Meta:
        db_table = 't_comment'
        verbose_name = 'Comment'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s owner:%s content:%s" % (self.id, self.owner, self.content)
        














    