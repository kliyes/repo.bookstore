#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import datetime

from django.db import models
from django.conf import settings

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


class CateManager(models.Manager):
    def getAllCates(self):
        '''获取所有分类'''
        return self.all()
    
    def get3Cates(self):
        '''获取先显示的3个分类, 文学, 小说, 艺术'''
        return [self.get(name='letter'), 
            self.get(name='novel'), Category.objects.get(name='art')]
    
    def getRestCates(self):
        '''获取除前3个之外的分类'''
        result = []
        for cate in self.all():
            if cate not in self.get3Cates():
                result.append(cate)
        return result

class Category(models.Model):
    '''定义书籍分类模型'''
    name = models.CharField(max_length=20)  # 名称
    label = models.CharField(max_length=20) # 显示的名称
    
    objects = CateManager()
    
    class Meta:
        db_table = 't_category'
        verbose_name = 'Category'
        app_label = 'books'
        
    def __unicode__(self):
        return u"id:%s name:%s" % (self.id, self.name)
    
    def getCount(self):
        return Book.objects.filter(category=self).count()
    
    def getPercent(self):
        '''获得该分类在书籍总数中所占比例'''
        return str((self.getCount()/float(Book.objects.totalBooks()))*100)+'%'
    
    def getHotBooks(self):
        '''获得当前分类下被购买次数最多的5本书籍'''
        return Book.objects.filter(category=self).order_by('-bought_count')[:5]


class BookManager(models.Manager):
    def getAll(self):
        return self.all()
    
    def totalBooks(self):
        return self.all().count()
    
    def getRecommend(self):
        '''获得最近登记的4本书籍作为推荐书籍'''
        return self.all().order_by('-reg_date')[:4]
    
    def getBestsellers(self, num=6):
        '''获得畅销书'''
        return self.all().order_by('-bought_count')[:num]
    
    def getHotTwoByCate(self, cate):
        '''按分类获取该分类下最热门两本书籍'''
        return self.filter(category=cate).order_by('-bought_count')[:2]
    
    
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
    spic = models.CharField(max_length=80, default=settings.DEFAULT_IMG) # 小图
    mpic = models.CharField(max_length=80) # 中图(书籍列表中显示)
    lpic = models.CharField(max_length=80) # 大图(书籍详情中显示)
    bought_count = models.IntegerField(default=0) # 被购次数
    category = models.ForeignKey(Category, null=True, blank=True) # 类别
    stock = models.IntegerField() # 库存
    publish_date = models.CharField(max_length=50) # 出版日期
    reg_date = models.DateTimeField(default=datetime.datetime.now) # 上架时间
    comment_count = models.IntegerField(default=0) # 被评论次数
    
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
    
    def getMarkedGrade(self, profile):
        '''获取某用户为本书的打分'''
        if profile in self.getMarkers():
            try:
                grade = Grade.objects.get(marker=profile, book=self)
            except Grade.DoesNotExist:
                return False
            return grade
        return False
    
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
        bookCmts = BookComment.objects.filter(book=self)
        for bookCmt in bookCmts:
            total += bookCmt.grade
        return total
    
    def getMarkersCount(self):
        '''获取打分人数'''
        return BookComment.objects.filter(book=self).count()
    
    def getAverage(self):
        '''获取平均分 总分除以总人数'''
        if self.getMarkersCount() != 0:
            return self.getTotalGrade()/self.getMarkersCount()
        return 0
    
    def addComment(self, profile, cmtContent):
        '''为书籍添加评论'''
        bookComment = BookComment(owner=profile, book=self, content=cmtContent)
        bookComment.save()
        self.comment_count += 1
        self.save()
        return bookComment

class Grade(models.Model):
    '''定义书籍得分模型'''
    marker = models.ForeignKey("profiles.Profile") # 打分用户
    book = models.ForeignKey(Book) # 打分书籍
    value = models.SmallIntegerField(default=5) # 用户对书籍打分的分值, 满分5分, 最少1分
    mark_date = models.DateTimeField(default=datetime.datetime.now) # 打分时间
    
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
    grade = models.SmallIntegerField(default=5) # 得分
    created_date = models.DateTimeField(default=datetime.datetime.now) # 评论时间
    
    class Meta:
        db_table = 't_bookcomment'
        verbose_name = 'BookComment'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s owner:%s content:%s" % (self.id, self.owner, self.content)


class Cart(models.Model):
    '''定义购物车模型'''
    owner = models.ForeignKey("profiles.Profile") # 购物车所属用户
    update_time = models.DateTimeField(auto_now=True) # 最后更新时间
    
    class Meta:
        db_table = 't_cart'
        verbose_name = 'Cart'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s owner:%s" % (self.id, self.owner)
    
    def getTotalFee(self):
        '''获取购物车中书籍总价'''
        totalFee = 0.0
        for item in self.getItems():
            totalFee += self.getItemFee(item.book)
        return totalFee
    
    def getItems(self):
        '''获取该购物车中所有项目'''
        return BookItem.objects.filter(cart=self)
    
    def getBooks(self):
        '''获取该购物车中的所有书籍'''
        books = []
        for item in self.getItems():
            books.append(item.book)
        return books
    
    def getItemByBook(self, book):
        '''根据Book获取该购物车中对应的一项'''
        try:
            bookItem = BookItem.objects.get(book=book)
        except BookItem.DoesNotExist:
            return None
        return bookItem
    
    def getItemFee(self, book):
        '''获得某一项的费用'''
        return self.getItemByBook(book).fee
    
    def addBookItem(self, book):
        '''向购物车中添加书籍'''
        bookItem = BookItem(cart=self, book=book, amount=1, fee=book.price)
        bookItem.save()
        book.stock -= 1
        book.save()
        return True
        
    def removeBookItem(self, book):
        '''从购物车中移除书籍'''
        bookItem = self.getItemByBook(book)
        bookItem.delete()
        book.stock += 1
        book.save()
        return True
    
    def moveToOrder(self, order):
        '''将购物车中项目转移到订单中'''
        for item in self.getItems():
            orderBookItem = OrderBookItem(order=order, book=item.book, 
                amount=item.amount, fee=item.fee)
            orderBookItem.save()
        return True
            
    def clearCart(self):
        '''清空购物车'''
        for item in self.getItems():
            item.delete()
        return True
        

class BookItem(models.Model):
    '''购物车中的某一项书籍'''
    cart = models.ForeignKey(Cart) # 项目所属购物车
    book = models.ForeignKey(Book) # 书籍
    amount = models.IntegerField(default=0) # 数量
    fee = models.FloatField(default=0.0) # 该项的小计
    
    class Meta:
        db_table = 't_book_item'
        verbose_name = 'BookItem'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s book:%s amount:%s fee:%s" % (self.id, self.book, 
            self.amount, self.fee)
    
    def setFee(self):
        '''计算小计'''
        self.fee = round(self.book.price * self.amount, 1)
        self.save()
        
    
class OrderManager(models.Manager):
    def getAll(self):
        '''获取所有订单'''
        return Order.objects.all()
    
    def totalOrders(self):
        '''订单总量'''
        return len(self.getAll())  
    
    def getOrdersByDate(self, fDate, tDate):
        '''按日期范围获取订单'''
        return Order.objects.filter(created_date__range=(fDate, tDate))
    
    def getDealOrders(self, orders):
        '''获得指定订单中交易完成的订单'''
        result = []
        for order in orders:
            if order.status == 1:
                result.append(order)
        return result
    
    def getCancelOrders(self, orders):
        '''获得指定订单中交易取消的订单'''
        result = []
        for order in orders:
            if order.status == 0:
                result.append(order)
        return result
    
    def getToSendOrders(self, orders):
        '''获得指定订单中等待发货的订单'''
        result = []
        for order in orders:
            if order.status == 2:
                result.append(order)
        return result
    
    def getToRecvOrders(self, orders):
        '''获得指定订单中等待收货的订单'''
        result = []
        for order in orders:
            if order.status == 3:
                result.append(order)
        return result
    

class Order(models.Model):
    '''定义订单模型'''
    owner = models.ForeignKey("profiles.Profile") # 订单所有者
    total_fee = models.FloatField() # 总金额
    is_charged = models.BooleanField(default=False) # 是否付款
    charge_type = models.SmallIntegerField(default=1) # 付款方式, 1-货到付款 2-在线支付
    status = models.SmallIntegerField(default=2) # 订单状态, -1-删除订单 1-完成交易 0-取消 2-等待发货 3-等待收货
    addr = models.CharField(max_length=200) # 送货地址
    contact = models.CharField(max_length=20) # 联系方式
    created_date = models.DateTimeField(default=datetime.datetime.now) # 订单生成时间
    updated_date = models.DateTimeField(default=datetime.datetime.now) # 订单更新时间
    
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
    
    def getItems(self):
        '''获得订单中所有的书籍项目'''
        return OrderBookItem.objects.filter(order=self)
    
    
class OrderBookItem(models.Model):
    '''订单中书籍项目模型'''
    order = models.ForeignKey(Order) # 订单
    book = models.ForeignKey(Book) # 书籍
    amount = models.IntegerField(default=0) # 数量
    fee = models.FloatField(default=0.0) # 该项的小计
    
    class Meta:
        db_table = 't_order_book'
        verbose_name = 'OrderBookItem'
        app_label = 'books'
    
    def __unicode__(self):
        return u"id:%s book:%s amount:%s fee:%s" % (self.id, self.book, 
            self.amount, self.fee)
    
    
    
    