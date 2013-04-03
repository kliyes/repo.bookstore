# -*-coding:utf-8 -*- 
import datetime
import ImageFile
import Image
import os
import uuid

from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext
from django.contrib import messages
from django.utils import simplejson as json
from django.core.urlresolvers import reverse

from profiles.models import City, Profile
from common import utils
from common.utils import ecode, jsonResponse
from activity.forms import ActivityForm
from activity.models import Activity, Comment

import logging
logger = logging.getLogger("mysite")


from common.consts import getActivityCategorys

#def pagingComments(request, actId):
#    '''分页活动评论'''
#    if not request.is_ajax():
#        raise Http404
#    
#    act = Activity.objects.get(id=int(actId))
#    pageNo = pages.getRequestPageNo(request)
#    
#    request.session[CURRENT_PAGENO_KEY] = pageNo
#    paging = pages.getSessionPaging(request, CMT_DATA_KEY)
#    if not paging:
#        cmtlist = act.getAllComments()
#        paging = initSessionCmtlistPaging(request, CMT_DATA_KEY, cmtlist, CMT_PAGE_SIZE)
#        
#    t = get_template(settings.TEMPLATE_COMMENT_LIST)
#    ctx = paging.result(pageNo)
#    
#    if request.user.is_authenticated() and request.user.get_profile():
#        request.user.get_profile().markAgreed(ctx["pageItems"].object_list)
#    
#    if pageNo == 1:
#        ctx.update(_handleCmtsPageOne(request, act))
#        
#    return utils.jsonResponse({'status': "success", 
#        'html': t.render(RequestContext(request, ctx))})



#@login_required
def goHome(request):
        
    latestActivities = Activity.objects.getLatestUpdatedActivities()
    hotestActivities = Activity.objects.getHotestActivities()
    
    return render_to_response(settings.TEMPLATE_HOME, RequestContext(request, {
        "latestActivities":latestActivities, "hotestActivities":hotestActivities,
        "cities": City.objects.exclude(id=1), "categorys": getActivityCategorys()}))

def getActivitesByCityCategory(request):
    cityId = request.GET.get('cityId', None)
    categoryId = request.GET.get('categoryId', None)
    
    city = None
    try:    
        city = City.objects.getById(id=cityId)
    except City.DoesNotExist:
        pass   
    
    try:
        latestActivities = Activity.objects.getLatestUpdatedActivitiesOnTerms(city, categoryId)
        hotestActivities = Activity.objects.getHotestActivitiesOnTerms(city, categoryId)
        latestTemplate = get_template(settings.TEMPLATE_LATEST_ACTIVITY)
        hotestTemplate = get_template(settings.TEMPLATE_HOTEST_ACTIVITY)
        latestHtml = latestTemplate.render(RequestContext(request,{"latestActivities":latestActivities}))
        hotestHtml = hotestTemplate.render(RequestContext(request,{"hotestActivities":hotestActivities}))
        return jsonResponse({"status": "0", "latestHtml":latestHtml, "hotestHtml":hotestHtml})
    except Exception, e:
        return jsonResponse({"status": "1"})
    
DRAFT_ACTIVITY_MARK = "draftActivity"    

@login_required
def createActivity(request):
    '''创建活动'''
    if request.method != "POST":
        return render_to_response(settings.TEMPLATE_CREATE_ACTIVITY, RequestContext(
            request, {"form": ActivityForm(profile=request.user.get_profile()), 
                      "cities": City.objects.getAll()}))

    # if POST request
    form = ActivityForm(request.POST)
    if form.is_valid():
        act = form.save(profile=request.user.get_profile())
        if act: 
            act.is_draft = True  
            act.save()
            request.session[DRAFT_ACTIVITY_MARK] = act 
            return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                    request, {"tmp_poster": settings.DEFAULT_POSTER}))
            #return HttpResponseRedirect(reverse("activity_upload_poster"))  # redirct to poster upload page     
    else:
        return HttpResponseRedirect(reverse("activity_create"))

from common import img_utils, file_utils
ACTIVITY_POSTER_ROOT = os.path.join(settings.PIC_ROOT, "activity")
DRAFT_POSTER_MARK = "draftPoster"
TMP_POSTER_MARK = "tmp_poster"

@login_required
def initPoster(request):
    '''上传活动海报'''
    
    tmp_poster = request.session.get(TMP_POSTER_MARK, None)
    if not tmp_poster:
        tmp_poster = settings.DEFAULT_POSTER 
    
    draftActivity = request.session.get(DRAFT_ACTIVITY_MARK, None)
    if not draftActivity:
        utils.addMsg(request, messages.INFO, u"请先创建活动")
        return render_to_response(settings.TEMPLATE_CREATE_ACTIVITY, RequestContext(
            request, {"form": ActivityForm(profile=request.user.get_profile()), 
                      "cities": City.objects.getAll()}))
        
    if request.method != "POST":
        if not draftActivity.tmp_poster:
            draftActivity.tmp_poster = draftActivity.big_poster
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
            request, {"tmp_poster": tmp_poster}))
        
    file = request.FILES["poster"]
    if not file:
        utils.addMsg(request, messages.ERROR, u"上传文件异常！")
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
    
    if (len(file) > settings.POSTER_UPPER_BOUND * 1024 * 1024):
        utils.addMsg(request, messages.ERROR, u"请确保上传的图片大小不超过5M！")
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
    
    fname, ext = os.path.splitext(str(file))
    if ext not in settings.ALLOWED_IMG_FORMAT:
        utils.addMsg(request, messages.ERROR, u"上传的图片格式不正确！")
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
    
    filename = img_utils.upload(file, settings.POSTER_SIZE_BIG, ACTIVITY_POSTER_ROOT, 100)
    
    if not filename:
        utils.addMsg(request, messages.ERROR, u"图片上传失败！")
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
    
    # tmp_poster临时存放上传的图片
    tmp_poster = "activity/%s" % (filename)
    request.session[TMP_POSTER_MARK] = tmp_poster 
    
    return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))


scalePic = img_utils.scalePic  
#未来的重构,上传和剪切考虑分成两个不同的页面   
def setPoster(request):
    '''裁剪活动海报'''
    
    tmp_poster = request.session.get(TMP_POSTER_MARK, None)
    print "from session:", tmp_poster
    if not tmp_poster:
        tmp_poster = settings.DEFAULT_POSTER 
    
    draftActivity = request.session.get(DRAFT_ACTIVITY_MARK, None)
    if not draftActivity:
        utils.addMsg(request, messages.INFO, u"请先创建活动")
        return render_to_response(settings.TEMPLATE_CREATE_ACTIVITY, RequestContext(
            request, {"form": ActivityForm(profile=request.user.get_profile()), 
                      "cities": City.objects.getAll()}))
        
    if request.method != 'POST':
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
    
    img = None
    try:
        img = img_utils.open(settings.PIC_ROOT, tmp_poster)
    except IOError, Exception:
        utils.addMsg(request, messages.ERROR, u"读取文件错误！")
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
        
    XY = ()
    try:            
        XY = (
            int(request.REQUEST.get("x1")), 
            int(request.REQUEST.get("y1")), 
            int(request.REQUEST.get("x2")),
            int(request.REQUEST.get("y2"))
        )
        logger.debug(XY)
    except Exception, e:
        logger.error(''+e)
        utils.addMsg(request, messages.WARNING, u"""还没有对海报进行剪切。剪切请在
            原海报上按住、并拖动鼠标。若不需要剪切，可点击'撤销'""")
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))
    
    img = img.crop(XY)
    
    # 缩放并新生成大,中,小三种尺寸图片
    big_poster = scalePic(img, settings.PIC_ROOT, "activity", utils.genUuid()+'_b', settings.POSTER_SIZE_BIG, 100)
    normal_poster = scalePic(img, settings.PIC_ROOT, "activity", utils.genUuid()+'_n', settings.POSTER_SIZE_NORMAL, 80)
    small_poster = scalePic(img, settings.PIC_ROOT, "activity", utils.genUuid()+'_s', settings.POSTER_SIZE_SMALL, 50)
    
    if big_poster and normal_poster and small_poster:
        
        ## 删除临时图片及设置之前的图片
        if tmp_poster != settings.DEFAULT_POSTER:
            file_utils.remove(settings.PIC_ROOT, tmp_poster)
                    
        request.session[TMP_POSTER_MARK] = big_poster 
        request.session[DRAFT_POSTER_MARK] = {
            "big_poster":    big_poster, 
            "normal_poster": normal_poster, 
            "small_poster":  small_poster, 
        }
        
        utils.addMsg(request, messages.SUCCESS, u"剪切海报成功")
        
        # set to draft acitivty 预览
        # TODO
        
        return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": big_poster}))
    
    utils.addMsg(request, messages.ERROR, u"添加海报失败")
    return render_to_response(settings.TEMPLATE_SET_POSTER, RequestContext(
                request, {"tmp_poster": tmp_poster}))


def doneActivityCreating(request):
    """提交活动"""
    draftActivity = request.session.get(DRAFT_ACTIVITY_MARK, None)
    if not draftActivity:
        utils.addMsg(request, messages.INFO, u"请先创建活动")
        return render_to_response(settings.TEMPLATE_CREATE_ACTIVITY, RequestContext(
            request, {"form": ActivityForm(profile=request.user.get_profile()), 
                      "cities": City.objects.getAll()}))
        
    draftPoster = request.session.get(DRAFT_POSTER_MARK, None)
    if draftPoster:
        draftActivity.big_poster = draftPoster["big_poster"]
        draftActivity.normal_poster = draftPoster["normal_poster"]
        draftActivity.small_poster = draftPoster["small_poster"]
        
    draftActivity.is_draft = False
    draftActivity.save()
    
    request.session[DRAFT_ACTIVITY_MARK] = None
    request.session[DRAFT_POSTER_MARK] = None
    request.session[TMP_POSTER_MARK] = None
    return render_to_response(settings.TEMPLATE_ACTIVITY_CREATE_DONE, RequestContext(
            request, {"act":draftActivity}))


from common.consts import CATEGORY_IT, CATEGORY_STARTUP, CATEGORY_COLLEGE, CATEGORY_OTHER

def detailActivity(request, actId):
    '''查看活动详情'''
    if not actId:
        raise Http404
    
    detailAct = None
    try:
        detailAct = Activity.objects.get(id=int(actId))
    except Activity.DoesNotExist:
        raise Http404
    
    if detailAct.category == 1:
        detailAct.categoryShow = CATEGORY_IT
    elif detailAct.category == 2:
        detailAct.categoryShow = CATEGORY_STARTUP
    elif detailAct.category == 3:
        detailAct.categoryShow = CATEGORY_COLLEGE
    elif detailAct.category == 99:
        detailAct.categoryShow = CATEGORY_OTHER   
    
    attended, interested = False, False 
    comments = detailAct.getAllComments()
    mostAgreedComments = detailAct.getMostAgreedComments()
    for cmt in comments:
        if cmt in mostAgreedComments:
            cmt.isTop = True
        else:
            cmt.isTop = False
    
    # 判断当前登录用户活动参加状态,感兴趣状态及赞成的评论状态
    if request.user.is_authenticated() and request.user.get_profile():
        attendedActivities = request.user.get_profile().getJoinedActivities()
        for act in attendedActivities:
            if detailAct.id == act.id:
                attended = True
                break
        likedActivities = request.user.get_profile().getLikedActivities()   
        for act in likedActivities:
            if detailAct.id == act.id:
                interested = True
                break 
            
        myAgreedComments = request.user.get_profile().getAgreedComments()
        for cmt1 in mostAgreedComments:
            if cmt1 in myAgreedComments:
                cmt1.agreed = True
            else:
                cmt1.agreed = False
                
        for cmt in comments:
            if cmt in myAgreedComments:
                cmt.agreed = True
                if cmt in mostAgreedComments:
                    cmt.isTop = True
                else:
                    cmt.isTop = False
            else:
                cmt.agreed = False
                if cmt in mostAgreedComments:
                    cmt.isTop = True
                else:
                    cmt.isTop = False
                    
    return render_to_response(settings.TEMPLATE_ACTIVITY_DETAIL, RequestContext(
        request, {"detailAct": detailAct, "comments": comments, 
                  "mostAgreedComments": mostAgreedComments, "attended": attended, 
                  "interested": interested}))

## following four methods can be replaced with only one generic method , TODO
@login_required
def joinActivity(request, actId):
    '''参加活动'''
    act = Activity.objects.get(id=actId)
    if request.user.get_profile().joinActivity(act):
        return HttpResponse(json.dumps({'status':'success'}))
    
    return HttpResponse(json.dumps({'status':'failed'}))
   
def quitActivity(request, actId):
    '''退出活动'''
    act = Activity.objects.get(id=actId)
    if request.user.get_profile().quitActivity(act):
        return HttpResponse(json.dumps({'status':'success'}))
    
    return HttpResponse(json.dumps({'status':'failed'}))    
    
def likeActivity(request, actId):
    '''对活动感兴趣'''
    act = Activity.objects.get(id=actId)
    if request.user.get_profile().likeActivity(act):
        return HttpResponse(json.dumps({'status':'success'}))
    
    return HttpResponse(json.dumps({'status':'failed'}))  

#@@ensure_csrf_cookie
def dislikeActivity(request, actId):
    '''对活动执行不感兴趣操作'''
    act = Activity.objects.get(id=actId)
    if request.user.get_profile().dislikeActivity(act):
        return HttpResponse(json.dumps({'status':'success'}))
    
    return HttpResponse(json.dumps({'status':'failed'}))

@login_required
def agreeComment(request, cmtId):
    '''对评论执行置顶操作'''
    profile = request.user.get_profile()
    cmt = Comment.objects.get(id=cmtId)
    if cmt.publisher != profile:            # 不能顶自己发表的评论
        if profile.agreeComment(cmt):
            return HttpResponse(json.dumps({'status':'success'}))
    
    return HttpResponse(json.dumps({'status':'failed'}))
    

@login_required
def addComment(request, actId):
    '''添加活动评论'''
    try:
        _content = request.POST.get("content",'')
        act = Activity.objects.get(id=actId)
        act.addComment(publisher=request.user.get_profile(), content=_content)
    except Exception, e:
        logger.error("%s" % e)
        return HttpResponse(json.dumps({'status':'failed'}))
      
    return HttpResponse(json.dumps({'status':'success'}))

def getOnesActivities(request, profileId):
    """获取个人活动列表,包括:发布的,参加的,及感兴趣的活动"""
    
    profile = None
    if request.user.is_authenticated() and request.user.get_profile().id == profileId:
        profile = request.user.get_profile()
    else:
        profile = Profile.objects.get(id=profileId)
        
    publishedActivities = profile.getPublishedActivities()
    joinedActivities = profile.getJoinedActivities()
    likedActivities = profile.getLikedActivities()    
    
    return render_to_response("activity/includes/activity_list_test.html", RequestContext(request, { 
        "publishedActivities": publishedActivities,
        "joinedActivities": joinedActivities,
        "likedActivities": likedActivities,})
    )    
    


