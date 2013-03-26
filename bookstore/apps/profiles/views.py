#coding=utf-8

from PIL import Image, ImageFile
from common import img_utils, file_utils, utils
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext
from profiles.forms import ProfileForm
from profiles.models import Profile, Following, City, Tag
import logging
import os
import uuid



logger = logging.getLogger("mysite")

@login_required
def addTag(request):
    """添加个性标签"""
    template = "profiles/tag.html"
    if request.method != 'POST':
        ownedTags = request.user.get_profile().getOwnedTags()
        return render_to_response(template, RequestContext(request, {
            "tags": request.user.get_profile().getNotOwnedTags(ownedTags), 
            "ownedTags": ownedTags}))
    
    tagId = request.REQUEST.get("tagId", "")
    tag = None
    try:
        tag = Tag.objects.get(id=tagId)
    except Tag.DoesNotExist:
        return utils.jsonResponse({"status": "-1", "msg": "tag %s not exist" % tagId})
    if request.user.get_profile().addTag(tag):
        return utils.jsonResponse({"status": "0", "msg": "Add tag success"})
    return utils.jsonResponse({"status": "-1", "msg": "Add tag failed"})       
    
@login_required
def removeTag(request):
    """删除个性标签"""
    tag = None
    tagId = request.REQUEST.get("tagId", "")
    try:
        tag = Tag.objects.get(id=tagId)
    except Tag.DoesNotExist:
        return utils.jsonResponse({"status": "-1", "msg": "tag %s not exist" % tagId})
    if request.user.get_profile().removeTag(tag):
        return utils.jsonResponse({"status": "0", "msg": "Remove tag success"})
    return utils.jsonResponse({"status": "-1", "msg": "Remove tag failed"})       


def goUserHome(request, profileId):
    """访问用户个人主页,以该函数为壳, 若website存在,则通过个性域名访问个人主页,否则通过用户
        id访问个人主页
    """
    
    try:
        profile = Profile.objects.get(id=profileId)
        if profile.website:
            return HttpResponseRedirect(reverse("profiles_user_website", args=[profile.website]))
        return _userPage(request, profile)
    except Profile.DoesNotExist:
        raise Http404    

def userPagePro(request, website):
    """通过个性域名访问用户个人主页"""
    try:
        profile = Profile.objects.get(website__iexact=website)
        return _userPage(request, profile)
    except Profile.DoesNotExist:
        raise Http404

#added by tom.jing for userPage test
def _userPage(request, profile):
    """通过用户id访问其个人主页, 私有函数
    """
    
    if request.user.is_authenticated() and request.user.get_profile() == profile:
        taProfile = None
    else:
        taProfile = profile

    publishedActivities = profile.getPublishedActivities()
    joinedActivities = profile.getJoinedActivities()
    likedActivities = profile.getLikedActivities() 
    
    return render_to_response(settings.TEMPLATE_USER_PAGE, RequestContext(request, { 
        "publishedActivities": publishedActivities,
        "joinedActivities": joinedActivities,
        "likedActivities": likedActivities,
        "taProfile": taProfile})
    )   

@login_required
def setProfile(request, **kwargs):
    """用户profile设置"""
    
    template = kwargs.pop("template", settings.TEMPLATE_SETTINGS)
    
    if request.method == "POST":
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            profile = form.save(request)
            if profile:
                utils.addMsg(request, messages.SUCCESS, ugettext(u"更新设置成功."))
                return HttpResponseRedirect(reverse("profiles_setting"))
    else :
        draftProfile = request.session.get("draftProfile", None)
        form = ProfileForm(user=request.user, draftProfile=draftProfile)
        
        if draftProfile:
            request.session["draftProfile"] = None
        
    return render_to_response(template, 
        RequestContext(request, {"form": form, 
            "cities": City.objects.getAll(),   #TODO 单独提取出作一个请求
        }))  

def changeCity(request, cityId):
    """更新所在城市"""
    profile = request.user.get_profile()
    profile.city = City.objects.getById(id=int(cityId)) 
    profile.save()
    return HttpResponseRedirect(reverse("profiles_setting"))

DRAFT_PROFILE_KEY = "draftProfile"

# 设置图片或密码前,保存已输入的profile信息草稿
def save_profile(request):
    profile = Profile()
    profile.name = request.POST["tmp_name"]
    profile.website = request.POST["tmp_website"]
    profile.spacename = request.POST["tmp_spacename"]
    profile.desc = request.POST["tmp_desc"]
    profile.city_id = request.POST["tmp_city"]
    profile.sex = request.POST["tmp_sex"]
    request.session[DRAFT_PROFILE_KEY] = profile 
    
    next = request.POST.get("next", '')
    if not next:
        raise Exception("No any next page")
    return HttpResponseRedirect(next)


PIC_ROOT = os.path.join(settings.MEDIA_ROOT, "img")
PROFILE_PIC_ROOT = os.path.join(PIC_ROOT, "profile")

def cancelPicSetup(request):
    '''撤销设置图片, 删除临时上传的图片'''
    
    profile = request.user.get_profile()
    
    if profile.tmp_pic and profile.tmp_pic != settings.DEFAULT_PIC and profile.tmp_pic != profile.big_pic:
        try:
            os.remove(os.path.join(PIC_ROOT, profile.tmp_pic))
            logger.debug("Deleted picture %s successfully" % profile.tmp_pic)
        except OSError:
            logger.debug("Picture %s not found when deleted" % profile.tmp_pic)
    
    profile.tmp_pic = None
    profile.save()
    return HttpResponseRedirect(reverse("profiles_setting"))

def initPic(request, template=settings.TEMPLATE_SETUP_PICTURE, **kwargs):
    '''处理用户上传头像图片，或用户已有头像初始化显示'''

    if request.method != "POST":
        profile = request.user.get_profile()
        if not profile.tmp_pic:
            profile.tmp_pic = profile.big_pic
            profile.save() 
        return render_to_response(settings.TEMPLATE_SETUP_PICTURE, RequestContext(request,))
    
    # 处理POST请求,文件上传，存储
    file = request.FILES["picture"]
    
    if not file:
        return HttpResponseRedirect(reverse("profiles_setpic"))
    
    if (len(file) > settings.PIC_UPPER_BOUND * 1024 * 1024):
        utils.addMsg(request, messages.ERROR, u"请确保上传的图片大小不超过2M！")
        return HttpResponseRedirect(reverse("profiles_setpic"))
    
    fname, ext = os.path.splitext(str(file))
    if ext not in settings.ALLOWED_IMG_FORMAT:
        utils.addMsg(request, messages.ERROR, u"上传的图片格式不正确！")
        return HttpResponseRedirect(reverse("profiles_setpic"))
    
    filename = img_utils.upload(file, settings.PIC_SIZE_BIG, PROFILE_PIC_ROOT, 100)
    
    if not filename:
        utils.addMsg(request, messages.ERROR, u"图片上传失败！")
        return HttpResponseRedirect(reverse("profiles_setpic"))
    
    profile = request.user.get_profile()
    
    # tmp_pic临时存放上传的图片
    profile.tmp_pic = "profile/%s" % (filename)
    profile.save()
    
    return HttpResponseRedirect(reverse("profiles_setpic"))


def setPic(request, template=settings.TEMPLATE_SETTINGS):
    """切剪并设置头像"""
    
    profile = request.user.get_profile()

    if not profile.tmp_pic:
        profile.tmp_pic = profile.big_pic
        profile.save()
    
    if request.method != 'POST':
        return render_to_response(settings.TEMPLATE_SETUP_PICTURE, RequestContext(request,))
    
    img = None
    try:
        img = img_utils.open(PIC_ROOT, profile.tmp_pic)
    except IOError, Exception:
        utils.addMsg(request, messages.ERROR, u"读取文件错误！")
        return HttpResponseRedirect(reverse("profiles_setpic"))
        
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
        utils.addMsg(request, messages.WARNING, u"""还没有对头像进行剪切。剪切请在
            大头像上按住、并拖动鼠标。若不需要剪切，可点击'撤销'""")
        return HttpResponseRedirect(reverse("profiles_setpic")) 
    
    img = img.crop(XY)
    
    big_pic = img_utils.scalePic(img, PIC_ROOT, "profile", utils.genUuid()+'_b', settings.PIC_SIZE_BIG, 100)
    normal_pic = img_utils.scalePic(img, PIC_ROOT, "profile", utils.genUuid()+'_n', settings.PIC_SIZE_NORMAL, 80)
    small_pic = img_utils.scalePic(img, PIC_ROOT, "profile", utils.genUuid()+'_s', settings.PIC_SIZE_SMALL, 50)
    
    if big_pic and normal_pic and small_pic:
        
        ## 删除临时图片及设置之前的图片
        if profile.tmp_pic != settings.DEFAULT_PIC:
            file_utils.remove(PIC_ROOT, profile.tmp_pic)
            
        file_utils.remove(PIC_ROOT, profile.big_pic)
        file_utils.remove(PIC_ROOT, profile.normal_pic)
        file_utils.remove(PIC_ROOT, profile.small_pic)
        
        profile.tmp_pic = big_pic
        profile.big_pic = big_pic
        profile.normal_pic = normal_pic
        profile.small_pic = small_pic
        profile.save()
        
        utils.addMsg(request, messages.SUCCESS, u"头像更新成功")
        return HttpResponseRedirect(reverse("profiles_setting"))
    
    utils.addMsg(request, messages.ERROR, u"更新头像失败")
    return HttpResponseRedirect(reverse("profiles_setpic"))
    

      
        
        
        
        
        
        
