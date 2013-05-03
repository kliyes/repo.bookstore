#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.db import models

from profiles.models import Profile

class FeedbackManager(models.Manager):
    def getAllFeedbacks(self):
        return Feedback.objects.all().order_by('-created_date')

class Feedback(models.Model):
    contact = models.CharField(max_length=80, null=True, blank=True)   
    content = models.CharField(max_length=800)
    created_date = models.DateTimeField()
    profile = models.ForeignKey(Profile, null=True, blank=True)
    
    objects = FeedbackManager()
    
    class Meta:
        db_table = 't_feedback'
        verbose_name = 'Feedback'
        app_label = 'sites'


class MottoManager(models.Manager):
    def getCount(self):
        return self.all().count()

class Motto(models.Model):
    '''定义注册登录页格言模型'''
    author = models.CharField(max_length=100, default='佚名') #格言作者
    content = models.CharField(max_length=500) #格言内容
    
    objects = MottoManager()
    
    class Meta:
        db_table = 't_motto'
        verbose_name = 'Motto'
        app_label = 'sites'
    
    
    
    
    
