# -*-coding:utf-8 -*-

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.models import User
from django.conf import settings

from idios.models import ProfileBase

#from common import utils

import logging
from books.models import BookComment, Cart, Order

logger = logging.getLogger("mysite")
NOTICE_UNREAD = 0
NOTICE_READ = 1

CITY_KEY_PREFIX = 'city_'
AREA_KEY_PREFIX = 'area_'
TAG_KEY_PREFIX  = 'tag_'

class Province(models.Model):
    name = models.CharField(max_length=40)
    desc = models.TextField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 't_province'
        verbose_name = 'Province'  

class CityManager(models.Manager):
    def getById(self, id):
        if not settings.CACHED_CITIES:
            initGlobalCityData()
        return settings.CACHED_CITIES.get("%s%s" % (CITY_KEY_PREFIX, id), None)
    
    def getAll(self):
        '''得到所有城市'''
        if not settings.CACHED_CITIES:
            initGlobalCityData()
        return settings.CACHED_CITIES.values() 
    
    def getAllAreas(self, city):
        '''获取某城市所有区域'''
        return city.getAllAreas()

class City(models.Model):
    name = models.CharField(max_length=40)
    province = models.ForeignKey(Province, null=True, blank=True)
    
    objects = CityManager()
    
    class Meta:
        db_table = 't_city'
        verbose_name = 'City'
    
    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)
    
    def getAllAreas(self):
        if not settings.CACHED_AREAES:
            initGlobalAreaData()
        allareas = settings.CACHED_AREAES.values()
        
        resultAreas = []
        for current in allareas:
            if current.city == self:
                resultAreas.append(current) 
        return resultAreas  

class Area(models.Model):
    '''城市区域'''
    name = models.CharField(max_length=40)
    city = models.ForeignKey(City)
    
    objects = CityManager()
    
    class Meta:
        db_table = 't_area'
        verbose_name = 'Area'
    
    def __unicode__(self):
        return u"%s %s %s" % (self.id, self.name, self.city.name)

    def getCity(self):
        return self.city

class Tag(models.Model):
    """个人标签"""
    name = models.CharField(max_length=40)
    label = models.CharField(max_length=50)
    type = models.IntegerField(default=0)     #标签类型
    
    class Meta:
        db_table = 't_tag'
        verbose_name = 'Personal Tag'
        
    def __unicode__(self):
        return self.name, self.label   
    
#############################################
# Initialize global data
#############################################
def initGlobalCityData():
    cities = City.objects.exclude(id=1)
    for city in cities:
        settings.CACHED_CITIES["%s%s" % (CITY_KEY_PREFIX, city.id)] = city
    
    logger.info("====> Global city data initialized")    

def initGlobalAreaData():    
    areas = Area.objects.all()
    for area in areas:
        settings.CACHED_AREAES["%s%s" % (AREA_KEY_PREFIX, area.id)] = area  
    logger.info("====> Global area data initialized")   
    
def initGlobalTagData():    
    tags = Tag.objects.all()
    for tag in tags:
        settings.CACHED_TAGS["%s%s" % (TAG_KEY_PREFIX, tag.id)] = tag  
    logger.info("====> Global personal tag data initialized")      

#initGlobalCityData()
#initGlobalAreaData()   
#initGlobalTagData()
        

class ProfileManager(models.Manager):
    def totalUsers(self):
        return Profile.objects.all().count()
    
class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, default='', null=True, blank=True)        #昵称
    desc = models.TextField(_("about"), max_length=200, default='', null=True, blank=True)      #个人介绍
    city = models.ForeignKey(City, null=True, blank=True)                                       #城市
    sex = models.CharField(_("sex"), default="unknown", max_length=20, null=True, blank=True)   #性别
    website = models.CharField(max_length=40, null=True, blank=True)                            #个性域名
    
    # user's pic
    big_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC)                                  
    normal_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC_NORMAL)                          
    small_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC_SMALL)  
    
    # 为临时保存用户上传的头像图片,添加该字段
    tmp_pic = models.CharField(max_length=80, default=settings.DEFAULT_PIC, null=True, blank=True)          #临时头像文件
    
    is_authed = models.BooleanField()                               #是否认证用户, 0-未认证 1-已认证
    is_organ = models.BooleanField()                                #是否是机构,0-个人 1-机构
    login_count = models.IntegerField(default=0)                    #登录次数
    
    # user's spacename
    spacename = models.CharField(max_length=50, null=True, blank=True)
    
    #===============================================
    #code in bookstore
    contact = models.CharField(max_length=20) # 联系方式（手机号码）
    addr = models.CharField(max_length=200) # 送货地址
    #===============================================
    
#    attend_activities = models.ManyToManyField(
#        "activity.Activity", 
#        related_name="attendActivities", 
#        verbose_name=u"用户参加的活动列表"
#    )
#    
#    interested_activities = models.ManyToManyField(
#        "activity.Activity", 
#        related_name="interestedActivities", 
#        verbose_name=u"用户感兴趣的活动列表"
#    )
#    
#    agreed_comments = models.ManyToManyField(
#        "activity.Comment", related_name="agreedComments", 
#        verbose_name=u"用户赞成的评论列表"
#    )
    
    tags = models.ManyToManyField(
        Tag, related_name="tags", 
        verbose_name=u"个性标签"
    )
    
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
    #===============================================
    
    def addTag(self, tag):
        self.tags.add(tag)
        return True
    
    def addTags(self, tags):   # debug TODO...
        self.tags.update(tags)
        return True
    
    def removeTag(self, tag):
        self.tags.remove(tag)
        return True
    
    def getOwnedTags(self):
        return self.tags.all()
    
    def getNotOwnedTags(self, ownedTags):
        ids = []
        if not ownedTags:
            ownedTags = self.getOwnedTags()
        for tag in ownedTags:
            ids.append(tag.id)
        return Tag.objects.filter(~Q(id__in=ids))
    
    def getAgreedComments(self):
        return self.agreed_comments.all()
    
#    def getJoinedActivities(self):
#        return self.attend_activities.all()
#    
#    def getLikedActivities(self):
#        return self.interested_activities.all()
#    
#    def getPublishedActivities(self):
#        from activity.models import Activity
#        return Activity.objects.filter(publisher=self)
    
#    def joinActivity(self, act):
#        '''参加活动'''
#        try:
#            self.attend_activities.add(act)
#            act.attendee_count += 1
#            act.save()
#            return True
#        except:
#            logger.warning("Profile %s joins into activity %s exception" % (self.id, act.id))
#            return False
#    
#    def quitActivity(self, act):
#        try:
#            self.attend_activities.remove(act)
#            act.attendee_count -= 1
#            act.save()
#            return True
#        except:
#            logger.warning("Profile %s quit activity %s exception" % (self.id, act.id))
#            return False
#        
#    def likeActivity(self, act):
#        try:
#            self.interested_activities.add(act)
#            act.like_count += 1
#            act.save()
#            return True
#        except:
#            logger.warning("Profile %s liking activity %s exception" % (self.id, act.id))
#            return False   
#        
#    def dislikeActivity(self, act):
#        try:
#            self.interested_activities.remove(act)
#            act.like_count -= 1
#            act.save()
#            return True
#        except:
#            logger.warning("Profile %s disliking activity %s exception" % (self.id, act.id))
#            return False       
        
    def agreeComment(self, cmt):
        try:
            self.agreed_comments.add(cmt)
            cmt.agree_count += 1
            cmt.save()
            return True
        except:
            logger.warning("Profile %s agree comment %s exception"% (self.id, cmt.id))
            return False
                 
        
class Following(models.Model):
    follower = models.ForeignKey(Profile, related_name='follower') #发起关注者
    followee = models.ForeignKey(Profile, related_name='followee') #被关注者
    direction = models.SmallIntegerField()                         #关注状况,0-双向关注 1-单向关注                
    
    class Meta:
        db_table = 't_following'
        verbose_name = 'Following'
    
    def __unicode__(self):
        return "follower-%s,followee-%s,direction-%s" % (self.follower, self.followee, self.direction)


    
    
