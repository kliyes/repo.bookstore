# -*-coding:utf-8 -*-
import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache  

from profiles.models import Profile, City, Area  
from common.decorators import cache_data
from common.utils import sort

import logging
logger = logging.getLogger("mysite")

ACTIVITY_TAG_KEY_PREFIX  = 'activity_tag_'

#最近更新活动最大个数
MAX_LATEST_ACTIVITIES = 30  
#最热活动最大个数
MAX_HOTEST_ACTIVITIES = 30  
#被顶次数最多的评论的最大个数
MAX_AGREED_COMMENTS = 5

class ActivityManager(models.Manager):
    
    @cache_data()
    def queryActivities(self, **params):
        '''按不同查询条件查询活动，city为必须传入的参数
        
            若city为空,则返回None
            可接受的参数如下:
                city:         城市
                area:         城市区域,如金牛区
                timeInterval:活动时间区间,如今天,明天,周末(周六,周日),最近一周等
                tag:          活动标签     
                sortedBy:     排序方式, 字符串类型,如published_date, price, attendee_count
        '''
        
        city = params.pop("city", None)
        if not city:
            logger.error("city passed is null when query activity by params ")
            return None
        
        kwargs = {'city': city}
        
        area = params.pop("area", None)
        timeInterval = params.pop("timeInterval", None)
        tag = params.pop("tag", None)
        #sortedBy = params.pop("sortedBy", None)
        
        logger.debug("query activities by params: city-%s, area-%s, timeInterval-%s, tag-%s" % (
            city, area, timeInterval, tag))
        
        if area:
            kwargs['area'] = area
        if timeInterval:
            kwargs['start_date__range'] = timeInterval
            # or useing following replace:
            # kwargs['start_date__gte'] = timeInterval[0]
            # kwargs['start_date__lte'] = timeInterval[1]
        
        actList = Activity.objects.filter(**kwargs)
        #print "SQL:", actList.query

        if tag:
            result = []
            for act in actList:
                if tag in act.getOwnedTags():
                    result.append(act)    
            return result    
        
        return actList   
    
    def sortActivities(self, actList, sortedBy):
        '''按活动发布时间, 参数人数, 价格等排序'''
        if sortedBy: 
            if sortedBy == 'published_date':
                actList = sorted(actList, key=lambda item: item.published_date, reverse=True)
            elif sortedBy == 'attendee_count':
                actList = sorted(actList, key=lambda item: item.attendee_count, reverse=True)
            elif sortedBy == 'price':
                actList = sorted(actList, key=lambda item: item.price, reverse=True)  
            logger.debug("activity list sorted by %s" % sortedBy)
        
        return actList    
    
    def searchActivities(self, keyword):
        '''Search activities by keyword, the keyword maybe included in the title or description of activity'''
        return Activity.objects.filter(Q(title__icontains=keyword) | Q(desc__icontains=keyword))
    
    def getLatestUpdatedActivities(self):
        '''get the date from cache later TODO '''
        
        # 经验证,可以先获取全部数据再进行过滤,排序等处理
        #tmpActs = Activity.objects.all()
        #return tmpActs.order_by('-last_updated')[:MAX_LATEST_ACTIVITIES]
        
        return Activity.objects.all().order_by('-last_updated')[:MAX_LATEST_ACTIVITIES]
    
    def getHotestActivities(self):
        '''get the date from cache later TODO '''
        return Activity.objects.all().order_by('-attendee_count', '-like_count')[:MAX_HOTEST_ACTIVITIES]
    
    def getHotestActivitiesOnTerms(self, _city, categoryId):
        '''get the hotest activities on terms'''
        #没有选择城市和分类，显示全国所有城市所有类别的最热活动
        if _city == '' and categoryId == '':
            return Activity.objects.getHotestActivities()
        #选择了城市，未选择分类，显示该城市所有类别的最热活动
        elif _city != '' and categoryId == '':
            return Activity.objects.filter(city=_city).order_by('-attendee_count', '-like_count')[:MAX_HOTEST_ACTIVITIES]
        #没有选择城市，选择了分类，显示全国所有符合该分类的最热活动
        elif _city == '' and categoryId != '':
            return Activity.objects.filter(category=categoryId).order_by('-attendee_count', '-like_count')[:MAX_HOTEST_ACTIVITIES]
        #选择了城市也选择了分类，显示该城市符合该分类的最热活动
        else:
            return Activity.objects.filter(city=_city, category=categoryId).order_by('-attendee_count', '-like_count')[:MAX_HOTEST_ACTIVITIES]
    
    def getLatestUpdatedActivitiesOnTerms(self, _city, categoryId):
        '''get the latest update activities on terms'''
        #没有选择城市和分类，显示全国所有城市所有类别的最近更新的活动
        
        if _city and categoryId:
            return Activity.objects.filter(city=_city, category=categoryId).order_by('-last_updated')[:MAX_LATEST_ACTIVITIES]
        
        if _city.id:
            return Activity.objects.filter(city=_city).order_by('-last_updated')[:MAX_LATEST_ACTIVITIES]
        
        if categoryId:            
            return Activity.objects.filter(category=categoryId).order_by('-last_updated')[:MAX_LATEST_ACTIVITIES]
        
        return Activity.objects.getLatestUpdatedActivities()

class ActivityTagManager(models.Manager):
    
    def getById(self, id):
        '''get tag by id'''
        if not settings.CACHED_ACTIVITY_TAGS:
            initGlobalActivityTagData()
        
        return settings.CACHED_ACTIVITY_TAGS.get("%s%s" % (ACTIVITY_TAG_KEY_PREFIX, id), None)
    
    def getRelatedTags(self, type):
        if not settings.CACHED_ACTIVITY_TAGS:
            initGlobalActivityTagData()
        tags = settings.CACHED_ACTIVITY_TAGS.values()
        
        result = []
        for tag in tags:
            if tag.type == type:
                result.append(tag)
        return result
    
    def removeRelatedTags(self, type):
        return ActivityTag.objects.filter(type=type).delete()
    
    def getTagsByIds(self, tagIds):
        if not settings.CACHED_ACTIVITY_TAGS:
            initGlobalActivityTagData()
        tags = settings.CACHED_ACTIVITY_TAGS.values()

        result = []
        for tag in tags:
            if tag.id in tagIds:
                result.append(tag)
        return result
    
class ActivityTag(models.Model):
    """活动可选用的标签"""
    name = models.CharField(max_length=40)    #name应使用英文
    label = models.CharField(max_length=50)
    type = models.IntegerField(default=0)     #标签分类
    
    objects = ActivityTagManager()
    
    class Meta:
        db_table = 't_activitytag'
        verbose_name = 'Activity Tag'
        
    def __unicode__(self):
        return "%s %s %s" % (self.id, self.name, self.label) 

class ActivityRoll(models.Model): 
    '''
    活动参加者花名册
    '''   
    title = models.CharField(max_length=40)
    created_date = models.DateTimeField(default=datetime.datetime.now())
    activity = models.OneToOneField('activity.Activity') 
    
    class Meta:
        db_table = 't_activity_roll'
        verbose_name = 'ActivityRoll'
        
    def __unicode__(self):    
        return "id:%s title:%s" % (self.id, self.title)
        
class RollItem(models.Model): 
    '''
    活动参加者信息填写项(花名册项)
    '''   
    roll = models.ForeignKey('activity.ActivityRoll')                       #条目所属花名册
    
    attendee = models.ForeignKey('profiles.Profile')                        #参加者profile
    name = models.CharField(max_length=50)                                  #参加者姓名
    age = models.IntegerField(default=0)                                    #参加者年龄
    phone = models.CharField(max_length=20, null=True, blank=True)          #参加者电话
    email = models.CharField(max_length=40, null=True, blank=True)          #参加者email
    occupation = models.CharField(max_length=40, null=True, blank=True)     #参加者职业
    
    class Meta:
        db_table = 't_rollitem'
        verbose_name = 'RollItem'
        
    def __unicode__(self):    
        return "id:%s name:%s" % (self.id, self.name)    

################################
# Initialize global data
################################    
def initGlobalActivityTagData():    
    tags = ActivityTag.objects.all()
    for tag in tags:
        settings.CACHED_ACTIVITY_TAGS["%s%s" % (ACTIVITY_TAG_KEY_PREFIX, tag.id)] = tag  
    logger.info("====> Global activity tag data initialized")      

#initGlobalActivityTagData() 

class Activity(models.Model):
    title = models.CharField(max_length=100)        #活动标题
    category = models.SmallIntegerField()           #活动类型,如IT, 创业者,大学生等
    publisher = models.ForeignKey(Profile)          #活动发布者
    city = models.ForeignKey(City, default=1)                                   #活动举办城市
    area = models.ForeignKey(Area, null=True, blank=True, default=5)            #活动举办所在区域，如成华区，金牛区等
    address = models.CharField(max_length=200, default='')                      #活动地址
    start_date = models.DateTimeField(default=datetime.datetime.now())          #活动开始时间
    end_date = models.DateTimeField(default=datetime.datetime.now())            #活动结束时间
    published_date = models.DateTimeField(default=datetime.datetime.now())      #活动发布时间
    last_updated = models.DateTimeField(default=datetime.datetime.now())        #活动信息最后更新时间
    price = models.FloatField(default=0)            #价格
    is_draft = models.BooleanField(default=False)   #是否草稿,默认为为正式发布
    is_audited = models.BooleanField(default=False) #是否已被审核, 默认未审核 
    
    #活动海报
    tmp_poster = models.CharField(max_length=80, default=settings.DEFAULT_POSTER)
    big_poster = models.CharField(max_length=80, default=settings.DEFAULT_POSTER)                                 
    normal_poster = models.CharField(max_length=80, default=settings.DEFAULT_POSTER_NORMAL)                           
    small_poster = models.CharField(max_length=80, default=settings.DEFAULT_POSTER_SMALL)                             
    
    desc = models.CharField(max_length=4000,  null=True, blank=True)        #活动信息文字介绍        
    attendee_count = models.IntegerField(default=0) #参加人数
    like_count = models.IntegerField(default=0)     #感兴趣人数
    coordinates = models.CharField(max_length=30, null=True, blank=True)    #活动地理坐标经纬度,如 (38.4627, 59.7823)
    
    organizer = models.CharField(max_length=200, null=True, blank=True)     #活动主办方
    roll = None        #活动参加者名单
    
    #活动标签
    tags = models.ManyToManyField(
        ActivityTag, related_name="tags", 
        verbose_name=u"活动标签"
    )
    
    objects = ActivityManager()
    
    class Meta:
        db_table = 't_activity'
        verbose_name = 'Activity'
        ordering = ['published_date']
    
    def addTag(self, tag):
        self.tags.add(tag)
        return True
    
    def addTags(self, tags):        # debug TODO...
        '''批量添加多个tag'''
        for tag in tags:
            self.addTag(tag)
        return True
    
    def removeTag(self, tag):
        self.tags.remove(tag)
        return True
    
    def removeTags(self, tags):
        '''批量删除tags(query_set object)'''
        for tag in tags:
            self.removeTag(tag)
        return True    
    
    def getOwnedTags(self):
        return self.tags.all()
    
    def getNotOwnedTags(self, ownedTags):
        ids = []
        if not ownedTags:
            ownedTags = self.getOwnedTags()
        for tag in ownedTags:
            ids.append(tag.id)
        return ActivityTag.objects.filter(~Q(id__in=ids))
                
    def addComment(self, **kwargs):
        cmt = Comment()
        cmt.publisher = kwargs.pop("publisher", None)
        cmt.content = kwargs.pop("content", None)
        cmt.activity = self
        cmt.created_date = datetime.datetime.now()
        cmt.save()
        
        return cmt
    
    def getMostAgreedComments(self):
        """取得被顶次数最多的评论"""
        return Comment.objects.filter(activity=self, agree_count__gt = 0).order_by('-agree_count')[:MAX_AGREED_COMMENTS]
    
    def getAllComments(self):
        return Comment.objects.filter(activity=self)
    
    def getCommentsCount(self):
        return Comment.objects.filter(activity=self).count()
        
    def deleteComment(self, commentId):
        pass
        
    ################################## 报名表
    def newEmptyRoll(self, title='A Roll'):
        '''创建一个空花名册.一个活动仅允许一个报名表'''
        if self.getRoll():
            raise Exception('The roll of activity %s has been existed. Only one roll allowed ' % self.id)
        
        roll = ActivityRoll(title=title, activity=self)
        roll.save()
        return roll
    
    def getRoll(self):
        '''获取活动参加者花名册object'''
        try:
            return ActivityRoll.objects.get(activity=self)
        except ActivityRoll.DoesNotExist:
            return None   
        
    def removeRoll(self):
        '''删除花名册: If this is called, the all related rollitems would be removed '''
        try:
            self.getRoll().delete()
            return True
        except ActivityRoll.DoesNotExist:
            return False  
    
    def getOrCreateRoll(self, title=''):
        '''若活动花名册存在,则直接返回该花名册,否则新创建一个空的花名册(没有参加者)'''
        roll = self.getRoll()
        if not roll:
            roll = self.newEmptyRoll(title=title)
        return roll    
    
    def addRollItem(self, **kwargs):
        '''向活动报名表(花名册)添加参加者'''
        rollItem = RollItem(**kwargs)
        rollItem.save()
        return rollItem  
    
    def removeRollItem(self, item):
        '''从花名册删除某个参加者'''
        return item.delete()
    
    def getRollItems(self):
        '''获取花名册中所有报名者'''
        return self.getRoll().rollitem_set.all()
    
    def __unicode__(self):
        return u"%s %s" % (self.id, self.title)
    
    def toJson(self):
        return {"id":self.id,
            "title":self.title,
            "category":self.category,
            "publisher":self.publisher.name,
            "city":self.city.name,
            "address":self.address,
            "start_date":str(self.start_date),
            "end_date":str(self.end_date),
            "last_updated":str(self.last_updated),
            "price":self.price,
            "poster_pic":self.poster_pic,
            "attendee_count":self.attendee_count,
            "like_count":self.like_count,
            "desc":self.desc
        }
    
class Comment(models.Model):
    publisher = models.ForeignKey(Profile, related_name="commenter") # 评论者
    activity = models.ForeignKey(Activity)          # 所评论的活动
    content = models.CharField(max_length=1000)     # 评论内容
    created_date = models.DateTimeField()           # 评论创建日期
    agree_count = models.IntegerField(default=0)    # 评论被顶次数
    
    # 被回复的评论, 该属性不空时,表示当前comment实体为一条回复 
    dest_comment = models.ForeignKey("activity.Comment", null=True, blank=True, related_name="comment_to") 
    
    class Meta:
        db_table = 't_comment'
        verbose_name = 'Comment'
        
    def __unicode__(self):
        return "id:%s publisher:(%s) dest_comment:(%s)" % (self.id, self.publisher, self.dest_comment)


    def isReply(self):
        '''当前对象是否一个回复'''
        return self.dest_comment
    
    def addReply(self, **kwargs):
        '''添加回复,必填参数:publisher, content'''
        cmt = Comment()
        cmt.publisher = kwargs.pop("publisher", None)
        cmt.content = kwargs.pop("content", None)
        cmt.activity = self.activity 
        cmt.created_date = datetime.datetime.now()
        cmt.dest_comment = self
        cmt.save()
        return cmt
    
    def getAllReplys(self):
        '''得到当前评论的所有回复'''
        return Comment.objects.filter(dest_comment=self)
    

    
    
    
       
