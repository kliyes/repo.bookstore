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
from django.conf import settings

'''
File feature description here
'''
class Author(models.Model):
    '''定义Author模型'''
    name = models.CharField(max_length=200) # 姓名
    desc = models.CharField(max_length=8000) # 简介
    work_count = models.IntegerField(default=1) # 作品数量
    
    class Meta:
        db_table = 't_author'
        verbose_name = 'Author'
        app_label = 'books'
        
    def __unicode__(self):
        return u"id:%s name:%s" % (self.id, self.name)
    
    def getBooks(self):
        return Book.objects.filter(author=self)


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
    name = models.CharField(max_length=800) # 书名
    author = models.ForeignKey(Author) # 作者
    price = models.FloatField() # 定价
    isbn = models.CharField(max_length=20) # ISBN号
    press = models.CharField(max_length=200) # 出版社
    desc = models.CharField(max_length=8000, blank=True, null=True) # 简介
    binding = models.CharField(max_length=10, blank=True, null=True) # 装潢类型, 精装或平装
    pages = models.CharField(max_length=9999) # 页数 
    img = models.CharField(max_length=80, default=settings.DEFAULT_IMG) # 图片
    bought_count = models.IntegerField(default=0) # 被购次数
    category = models.ForeignKey(Category, null=True, blank=True) # 类别
    stock = models.IntegerField() # 库存
    publish_date = models.CharField(max_length=50) # 出版日期
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
        return BookComment.objects.filter(book=self).order_by('-created_date')
    
    def getMarkers(self):
        '''获取打分用户'''
        markers = []
        grades = Grade.objects.filter(book=self)
        for grade in grades:
            markers.append(grade.marker)
        return markers
    
    def getTotalGrade(self):
        '''获取总分'''
        total = 0
        grades = Grade.objects.filter(book=self)
        for grade in grades:
            total += grade.value
        return total
    
    def getMarkersCount(self):
        '''获取打分人数'''
        return len(self.getMarkers())
    
    def getAverage(self):
        '''获取平均分 总分除以总人数'''
        if self.getMarkersCount() != 0:
            return self.getTotalGrade()/self.getMarkersCount()
        return 0
    

class Grade(models.Model):
    '''定义书籍得分模型'''
    marker = models.ForeignKey("profiles.Profile") # 打分用户
    book = models.ForeignKey(Book) # 打分书籍
    value = models.SmallIntegerField(default=5) # 用户对书籍打分的分值, 满分5分, 最少1分
    mark_date = models.DateTimeField(default=datetime.datetime.now()) # 打分时间
    
    class Meta:
        db_table = 't_grade'
        verbose_name = 'BookGrade'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s marker:%s value:%s" % (self.id, self.marker, self.value)


class BookComment(models.Model):
    '''定义评论模型'''
    owner = models.ForeignKey("profiles.Profile") # 评论发表者
    book = models.ForeignKey(Book) # 所评论的书籍
    content = models.CharField(max_length=1000) # 评论内容
    created_date = models.DateTimeField(default=datetime.datetime.now()) # 评论时间
    
    class Meta:
        db_table = 't_bookcomment'
        verbose_name = 'BookComment'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s owner:%s content:%s" % (self.id, self.owner, self.content)


class OrderManager(models.Manager):
    def totalOrders(self):
        '''订单总量'''
        return Order.objects.all().count()  
    
    def getOrdersByDate(self, fDate, tDate):
        '''按日期范围获取订单'''
        return Order.objects.filter(created_date__range=(fDate, tDate))

class Order(models.Model):
    '''定义订单模型'''
    owner = models.ForeignKey("profiles.Profile") # 订单所有者
    total_fee = models.FloatField() # 总金额
    is_charged = models.BooleanField(default=False) # 是否付款
    charge_type = models.SmallIntegerField(default=1) # 付款方式, 1-货到付款 2-在线支付
    status = models.SmallIntegerField(default=2) # 订单状态, 1-完成交易 0-取消 2-等待发货 3-等待收货 
    addr = models.CharField(max_length=200) # 送货地址
    created_date = models.DateTimeField(default=datetime.datetime.now()) # 订单生成时间
    
    books = models.ManyToManyField(
        "books.Book", related_name="book_books", 
        verbose_name=u"订单中的书目"
    )
    
    objects = OrderManager()
    
    class Meta:
        db_table = 't_order'
        verbose_name = 'Order'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s owner:%s total_fee:%s" % (self.id, self.owner, self.total_fee)
    
    def charge(self):
        self.is_charged = True
        self.save()
        return True
    
    def addBook(self, book):
        '''向订单中添加书籍'''
        self.book.add(book)
        book.bought_count -= 1
        return True
        
    def addBooks(self, books):
        '''批量添加书籍'''
        for book in books:
            self.addBook(book)
        return True
    
    def removeBook(self, book):
        '''从订单中移除书籍'''
        self.books.remove(book)
        book.bought_count += 1
        return True
    
    def removeBooks(self, books):
        '''从订单中批量移除书籍'''
        for book in books:
            self.removeBook(book)
        return True
    







    