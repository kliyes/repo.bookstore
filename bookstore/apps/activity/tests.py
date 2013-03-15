# -*-coding:utf-8 -*-

'''
Created on Nov 13, 2012

@author: junn
'''

from django.utils import unittest
from django.test.client import Client

from common import utils
from activity.models import Activity, ActivityTag, ActivityRoll, RollItem
from profiles.models import Area, City, Profile


class RollTest(unittest.TestCase):
    pId = 1
    
    def testNewEmptyRoll(self):
        '''为活动创建空的花名册'''
        act = self.activity
        
        self.assertIsNone(act.getRoll()) # initial, the roll is none
        
        act.newEmptyRoll(title='Test Roll')
        self.assertIsNotNone(act.getRoll())
        
        # clear data
        self.activity.removeRoll()
        self.assertIsNone(act.getRoll())
        
    def testGetRoll(self):
        '''查看报名表测试'''
        act = self.activity
        act.getOrCreateRoll(title='Test Roll')
        self.assertIsNotNone(act.getRoll())
        
        oriLen = len(act.getRollItems())
        act.addRollItem(
            roll=act.getRoll(),
            attendee=self.publisher,
            name='Testing Boy',
            age=29,
            phone='15882138964',
            email='hello@boy.com',
            occupation=u'coder'
        )
        rollItem = act.getRollItems()
        print 'rollItem', rollItem
        self.assertEquals(len(act.getRollItems()), oriLen+1)
        
        act.removeRoll()
        self.assertIsNone(act.getRoll())
        
    def testDeleteRoll(self):
        '''删除报名表测试'''    
        act = self.activity
        act.getOrCreateRoll(title='Test Roll')
        self.assertIsNotNone(act.getRoll())
        
        act.removeRoll()
        self.assertIsNone(act.getRoll())
    
    def testFillEntryform(self):   
        '''填写报名表测试'''
        act = self.activity
        act.getOrCreateRoll(title='Test Roll')
        self.assertIsNotNone(act.getRoll())
        
        oriLen = len(act.getRollItems())
        rollItem = act.addRollItem(
            roll= act.getRoll(),           
            attendee=self.publisher,
            name='Testing Boy',
            age=29,
            phone='15982249999',
            email='hello@boy.com',
            occupation=u'码农'
        )
        print 'new rollItem:', rollItem 
        self.assertEquals(len(act.getRollItems()), oriLen+1) 
        
        act.removeRollItem(rollItem)
        self.assertEquals(len(act.getRollItems()), oriLen)
        
        act.removeRoll()
        self.assertIsNone(act.getRoll())
        
    def setUp(self):
        '''initialize activity publisher and activity'''
        self.publisher = Profile.objects.get(id=self.pId)
        
        actList = Activity.objects.all()[:1]
        if not actList:
            act = Activity(
                title="test roll",
                category=1,
                publisher=Profile.objects.get(id=self.pId),
            )
            act.save()
            self.activity = act   
        else:
            self.activity = actList[0]  

            

class CommentTest(unittest.TestCase):
    def setUp(self):
        actList = Activity.objects.all()[:1]
        print "actList:", actList
        if not actList:
            act = Activity(
                title="test",
                category=1,
                publisher=Profile.objects.get(id=1),
            )
            act.save()
            print "activity newed", act
            self.activity = act   
            self.publisher = Profile.objects.get(id=1)
        else:
            self.activity = actList[0]  
            self.publisher = Profile.objects.get(id=1)  
    
    def testAddComment(self):
        '''添加评论'''
        originCount = len(self.activity.comment_set.all())
        newComment = self.activity.addComment(publisher=self.publisher, content="comment for testing")
        self.assertEqual(originCount+1, len(self.activity.comment_set.all()))
        
        newComment.delete()
        self.assertEqual(originCount, len(self.activity.comment_set.all()))
        
    def testAddReply(self):
        '''添加回复'''
        newComment = self.activity.addComment(publisher=self.publisher, content="comment for testing")
        
        # assert newComment is not a reply
        self.assertTrue(not newComment.dest_comment)
        
        newReply = newComment.addReply(publisher=self.publisher, content="reply for testing")
        
        # assert newReply is a reply
        self.assertTrue(newReply.dest_comment)
        
        self.assertEqual(newReply.dest_comment, newComment)
        self.assertTrue(newReply.dest_comment == newComment)

        newComment.delete()
        self.assertEqual(len(newComment.getAllReplys()), 0)
        
    def testGetReplys(self):
        newComment = self.activity.addComment(publisher=self.publisher, content="comment for testing")
        newReply = newComment.addReply(publisher=self.publisher, content="reply for testing")
        self.assertEqual(len(newComment.getAllReplys()), 1)
        self.assertEqual(newComment.getAllReplys()[0], newReply) 
        
        newComment.delete()           
        
    def testIsReply(self): 
        newComment = self.activity.addComment(publisher=self.publisher, content="comment for testing")
        newReply = newComment.addReply(publisher=self.publisher, content="reply for testing") 
        self.assertFalse(newComment.isReply())
        self.assertTrue(newReply.isReply())

class QueryActivityTest(unittest.TestCase):
    '''测试按不同查询条件查询活动'''
    
    def testGetActivitiesByCity(self):
        city = City.objects.getById(id=2)
        params = {"city": city}
        acts = Activity.objects.queryActivities(city=city, sortedBy='attendee_count')
        print "result len:", len(acts)
        for i in range(0, len(acts)):
            print "result activities: ", acts[i].title
        
        acts = Activity.objects.queryActivities(city=city, )
        
    def testSortActivities(self):
        city = City.objects.getById(id=2)
        params = {"city": city}
        acts = Activity.objects.queryActivities(city=city)
        acts = Activity.objects.sortActivities(acts, 'price')
        print "result len:", len(acts)
        print "result activities: ", acts
        
        acts = Activity.objects.queryActivities(city=city)
        acts = Activity.objects.sortActivities(acts, 'published_date')
        print "result len:", len(acts)
        print "result activities: ", acts
        
        acts = Activity.objects.queryActivities(city=city)
        acts = Activity.objects.sortActivities(acts, 'attendee_count')
        print "result len:", len(acts)
        print "result activities: ", acts

    def testGetActivitiesByCityArea(self):
        '''根据城市和区域查询'''
        city = City.objects.getById(id=2)
        area = Area.objects.get(id=1)
        acts = Activity.objects.queryActivities(city=city, area=area)
        print "result len:", len(acts)
        print "result activities: ", acts  

    def testGetActivitiesByTag(self):
        '''根据Tag查询活动'''
        city = City.objects.getById(id=2)

        # this week        
        timeInterval = (utils.monday(), utils.sunday())
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval)
        print "this week-->"        
        print "result len:", len(acts)
        print "result activities: ", acts
        
        tag = ActivityTag.objects.getById(id=1)
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval, tag=tag)
        print "this week in tag %s-->", tag        
        print "result len:", len(acts)
        print "result activities: ", acts   
        

    def testGetActivitiesByTime(self):
        '''根据时间区间查询活动'''
        city = City.objects.getById(id=2)

        # today        
        timeInterval = (utils.today(), utils.today())
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval)
        print "today-->"        
        print "result len:", len(acts)
        print "result activities: ", acts 

        # tomorrow
        timeInterval = (utils.tomorrow(), utils.tomorrow())
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval)
        print "tomorrow-->"
        print "result len:", len(acts)
        print "result activities: ", acts      
        
        # from start_date to end_date
        timeInterval = (utils.today(), utils.sunday())
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval)
        print "today-->sunday"
        print "result len:", len(acts)
        print "result activities: ", acts
        
        # this week all
        timeInterval = (utils.monday(), utils.sunday())
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval)
        print "this week-->"
        print "result len:", len(acts)
        print "result activities: ", acts             
        
        # weekends
        timeInterval = (utils.saturday(), utils.sunday())
        acts = Activity.objects.queryActivities(city=city, timeInterval=timeInterval)
        print "weekends-->"
        print "result len:", len(acts)
        print "result activities: ", acts 
              
    
    def testQueryActivityByParams(self):
        city = None
        area = Area.objects.get(id=1)
        
        actlist = Activity.objects.queryActivities(city=city, area=area)
        self.assertIsNone(actlist)
        
        city = City.objects.getById(id=2)
        area = Area.objects.getById(id=1)
        
        print "city %s, area %s" % (city, area)
        actlist = Activity.objects.queryActivities(city=city, area=area)
        print "actlist:", actlist    

class AreaTest(unittest.TestCase):
    def testGetActivityArea(self):
        actId = 1
        act = Activity.objects.get(id=actId) 
        print "act:", act
        
        print "activity area:", act.area      
        
    def testUpdateActivityArea(self):
        actId = 1
        act = Activity.objects.get(id=actId) 
        print "act:", act
        print "activity area:", act.area
        
        
        areaId = 1
        act.area = Area.objects.get(id=areaId)
        act.save()
        print "update area to %s, activity area: %s" % (areaId, act.area)

        areaId = 4
        act.area = Area.objects.get(id=areaId)
        act.save()
        print "update area to %s, activity area: %s" % (areaId, act.area)        
        
                         

class TagTest(unittest.TestCase):
    def testRelatedTags(self):
        '''获取指定类别的tag'''
        tag1 = ActivityTag(name="ren", label=u"天地人", type=99999)
        tag1.save()
        tag2 = ActivityTag(name="linyu", label=u"淋雨", type=99999)
        tag2.save()
        tag3 = ActivityTag(name="xianren", label=u"仙人", type=99999)
        tag3.save()
        
        tags = ActivityTag.objects.getRelatedTags(99999)
        self.assertEquals(len(tags), 3)
        
        tag1.delete()
        print "tag1 deleted"
        tag2.delete()
        print "tag2 deleted"
        tag3.delete()
        print "tag3 deleted"
        
#    def testRemoveRelatedTags(self):
#        '''删除指定类别的tag'''
#        type = 1
#        if ActivityTag.objects.removeRelatedTags(type):
#            self.assertEqual(ActivityTag.objects.filter(type=type), 0)
                
    def testAddTags(self):
        '''批量添加tag'''
        actId = 1
        act = Activity.objects.get(id=1)
        originTags = act.getOwnedTags()
        print "origin tags:", len(originTags), originTags
        
        # add tags
        newAddedTags = ActivityTag.objects.filter(type=1)
        print "new tags added:", len(newAddedTags), newAddedTags
        act.addTags(newAddedTags)
        
        afterTags = act.getOwnedTags()
        print "after added:", len(afterTags), afterTags
        self.assertEquals(len(afterTags) - len(originTags), len(newAddedTags))
        
        # delete the added tags just now
        act.removeTags(newAddedTags)
        
    def testGetTagsByIds(self):
        '''获取tags by ids'''
        tagIds = 1, 2, 3
        print ActivityTag.objects.getTagsByIds(tagIds)    
        
        tagIds = 5, 6, 7
        print ActivityTag.objects.getTagsByIds(tagIds)
    
    def testGetOwnedTags(self):
        actId = 1
        act = Activity.objects.get(id=actId) 
        print "act:", act
        
        print act.getOwnedTags()

    def testAddTag(self):
        actId = 1
        act = Activity.objects.get(id=actId) 
        print "act:", act
        print "owned tags:", act.getOwnedTags()
        
        tag1 = ActivityTag.objects.getById(id=1)
        print "add tag id=1:"
        act.addTag(tag1)
        print "owned tags:", act.getOwnedTags()
        
        tag2 = ActivityTag.objects.getById(id=2)
        print "add tag id=%s:", tag2.id
        act.addTag(tag2)
        print "owned tags:", act.getOwnedTags()
        
        act.removeTag(tag1)
        print "tag1 removed"
        print "owned tags:", act.getOwnedTags()
        
        act.removeTag(tag2)
        print "tag2 removed"
        print "owned tags:", act.getOwnedTags()        
        
    def testGetNotOwnedTags(self):
        actId = 1
        act = Activity.objects.get(id=actId) 
        print "act:", act
        print "owned tags:", act.getOwnedTags()
        
        tag1 = ActivityTag.objects.getById(id=1)
        print "add tag id=1:"
        act.addTag(tag1)
        print "owned tags:", act.getOwnedTags()
        
        print "not owned tags:", act.getNotOwnedTags(act.getOwnedTags())   
        
    def testGetAllTags(self):
        print "all activity tags:", ActivityTag.objects.all()    
        

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        #response = self.client.get('/customer/details/')

        # Check that the response is 200 OK.
        #self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 5 customers.
        #self.assertEqual(len(response.context['customers']), 5)
        
        pass
 
def test_something(self):
    session = self.client.session
    session['somekey'] = 'test'
    session.save() 
 
class HelloTest(unittest.TestCase):
    '''This is a sample test'''
    
    def testAdd(self):  ## test method names begin 'test*'
        self.assertEqual((1 + 1), 2)
        self.assertEqual(0 + 1, 1)
    
    def testTrueOrFalse(self):
        self.assertTrue(1 == 1) 
        self.assertTrue(1 != 2)
        
    def testMultiply(self):
        self.assertEqual((0 * 10), 0)
        self.assertEqual((5 * 8), 40)
        
    def setUp(self):
        pass
            
    def tearDown(self):   
        pass 

        