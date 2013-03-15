# -*-coding:utf-8 -*-
'''
Created on Jul 30, 2012

@author: junn
'''
from django.db import models

from profiles.models import Profile


#log = logging.getLogger("mysite")

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
    
    
