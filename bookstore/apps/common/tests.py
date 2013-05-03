#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from PIL import Image
import datetime

from django.utils import unittest
from django.test.client import Client
from django.core.cache import cache  

from common import img_utils, utils 
 
class CachedTest(unittest.TestCase):
    def testCacheStartup(self):
        cache.set('my_key', 'hello, world!', 30)  
        print "get from cache:", cache.get('my_key')  
        
    def clearCache(self):
        cache.set('my_key', 'hello, world!', 30)  
        cache.clear()
        print '======== Cache cleared ========='
        print "get from cache:", cache.get('my_key')    
 
class DateTest(unittest.TestCase):
    '''时间区间测试，如周末，一周之内'''
    
    def testToday(self):
        today = datetime.date.today() 
        print "today():", today
        
        print "weekday:", datetime.date.weekday(today) #返回整数，如0对应星期一，3对应星期四
        print "iso weekday：", datetime.date.isoweekday(today) #返回整数，如3对应星期三
        
        # tomorrow
        tomorrow = today + datetime.timedelta(days=1)
        print "tomorrow", tomorrow
        
        # weekends
        delta = 7 - datetime.date.isoweekday(today)
        satDay = today + datetime.timedelta(days=delta-1)
        sunDay = today + datetime.timedelta(days=delta)
        print "satDay:%s, sunDay:%s" % (satDay, sunDay)   
        
    def testDateInterval(self):
        '''获取时间间隔'''
        
        print "yesterday:", utils.yesterday()
        print "today:", utils.today()
        print u"星期几:", utils.weekday()
        print "tomorrow:", utils.tomorrow()
        print "(saturday, sunday):", utils.saturday(), utils.sunday()
        print "monday:", utils.monday()    
        
        # latest week
        print "latest week from monday to sunday: %s - %s" % (utils.monday(), utils.sunday())
 
class ImageTest(unittest.TestCase):
    '''This is a sample test'''
    imgPath = "/home/junn/Pictures/"
    tmpPath = "/home/junn/temp/"
    
    def testOpenImage(self):
        img = img_utils.open(self.imgPath, "yuanfang.png")
        print img.__class__
        self.assertTrue(isinstance(img, Image.Image))
        
        img1 = img_utils.open(self.imgPath, "xi-ma.jpeg")
        print img1.__class__
        self.assertTrue(isinstance(img1, Image.Image))
        
    def testSaveImage(self):
        img = img_utils.open(self.imgPath, "xi-ma.jpeg")
        self.assertTrue(img_utils._save(img, self.imgPath, "xi-ma-test.jpeg", create_dir=False))
        
        img1 = img_utils.open(self.imgPath, "xi-ma.jpeg")
        self.assertTrue(img_utils._save(img1, "/home/junn/temp/pic/", "xi-ma-test1.jpeg", create_dir=True))
    
    def testThumbImage(self):
        img = img_utils.open(self.imgPath, "xi-ma.jpeg")
        self.assertTrue(img_utils._thumb(img, (100, 100)))
        self.assertTrue(img_utils._save(img, self.imgPath, 'xi-ma-thumb.jpeg'))
        
    def testScaleImage(self):
        img = img_utils.open(self.imgPath, "xi-ma.jpeg")
        self.assertTrue(img_utils.scale(img, (128, 128), self.tmpPath, 100))
        
    def testCutImage(self):
        img = img_utils.open(self.imgPath, "xi-ma.jpeg") 
        self.assertTrue(img_utils.cut(img, (100, 100, 150, 150), (300, 300), self.tmpPath, 100))
        
    def testUploadImage(self):
        # i don't know how to build a django UploadedFile object, so it haven't 
        # been tested TODO
        try:
            self.assertTrue(img_utils.upload())
        except:
            pass    
                        
    
    def testAdd(self):  ## test method names begin 'test*'
        self.assertEqual((1 + 2), 3)
        self.assertEqual(0 + 1, 1)
        
    def setUp(self):
        pass
            
    def tearDown(self):   
        pass 

        