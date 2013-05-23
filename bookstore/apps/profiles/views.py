#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import logging
import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext

from PIL import Image, ImageFile

from common import img_utils, file_utils, utils, pages
from profiles.forms import ProfileForm
from profiles.models import Profile, Following, City, Tag
from books.models import Order
from django.template.loader import get_template
import json
from BeautifulSoup import BeautifulSoup



logger = logging.getLogger("mysite")

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
            
        else:
            soup = BeautifulSoup(str(form.errors))
            utils.addMsg(request, messages.ERROR, soup.ul.li.ul.li.contents[0])
#            utils.addMsg(request, messages.ERROR, form.errors)
        
    else :
        draftProfile = request.session.get("draftProfile", None)
        form = ProfileForm(user=request.user, draftProfile=draftProfile)
        
        if draftProfile:
            request.session["draftProfile"] = None
            
    return render_to_response(template, 
        RequestContext(request, {"form": form}))  


DRAFT_PROFILE_KEY = "draftProfile"
# 设置图片或密码前,保存已输入的profile信息草稿
def save_profile(request):
    profile = Profile()
    profile.name = request.POST["tmp_name"]
    profile.desc = request.POST["tmp_desc"]
    profile.addr = request.POST["tmp_addr"]
    profile.contact = request.POST["tmp_contact"]
    profile.receiver = request.POST["tmp_receiver"]
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

@login_required
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

@login_required
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
            int(request.REQUEST.get("x1", '0')), 
            int(request.REQUEST.get("y1", '0')), 
            int(request.REQUEST.get("x2", '50')),
            int(request.REQUEST.get("y2", '50'))
        )
        if XY[0] == XY[2] and XY[1] == XY[3]:
            raise Exception
        img = img.crop(XY)
    except:
        utils.addMsg(request, messages.WARNING, u"""还没有对头像进行剪切。剪切请在
            大头像上按住、并拖动鼠标。若不需要剪切，可点击'撤销'""")
        return HttpResponseRedirect(reverse("profiles_setpic")) 
    
    
    big_pic = img_utils.scalePic(img, PIC_ROOT, "profile", utils.genUuid()+'_b', settings.PIC_SIZE_BIG, 100)
    normal_pic = img_utils.scalePic(img, PIC_ROOT, "profile", utils.genUuid()+'_n', settings.PIC_SIZE_NORMAL, 80)
    small_pic = img_utils.scalePic(img, PIC_ROOT, "profile", utils.genUuid()+'_s', settings.PIC_SIZE_SMALL, 50)
    
    if big_pic and normal_pic and small_pic:
        
        ## 删除临时图片及设置之前的图片
        if profile.tmp_pic != settings.DEFAULT_PIC:
            file_utils.remove(PIC_ROOT, profile.tmp_pic)
        
        if profile.big_pic != settings.DEFAULT_PIC:
            file_utils.remove(PIC_ROOT, profile.big_pic)
        if profile.normal_pic != settings.DEFAULT_PIC_NORMAL:
            file_utils.remove(PIC_ROOT, profile.normal_pic)
        if profile.small_pic != settings.DEFAULT_PIC_SMALL:
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


def initSessionOrderlistPaging(request, dataKey, orderlist, pageSize):
    ''''''
    return pages.setSessionPaging(request, dataKey, orderlist, pageSize)

@login_required    
def checkOrders(request):
    '''查看用户订单'''
    profile = request.user.get_profile()
    
    orders = profile.getOrders().exclude(id__in=profile.delOrderIds).order_by('-created_date')
    ctx = {}
    
    orderPaging = initSessionOrderlistPaging(request, 'orderData', orders, 5)
    if orderPaging:
        ctx.update(orderPaging.result(1)) 
    
    return render_to_response('profiles/user_orders.html', RequestContext(request, ctx))
    
def pagingOrders(request):
    '''分页订单, ajax request only'''
    if not request.is_ajax():
        raise Http404
    
    profile = request.user.get_profile()
    
    pageNo = pages.getRequestPageNo(request)
    request.session['currentPageNo'] = pageNo
    paging = pages.getSessionPaging(request, 'orderData')
    if not paging:
        orderlist = profile.getOrders().exclude(id__in=profile.delOrderIds)
        paging = initSessionOrderlistPaging(request, 'orderData', orderlist, 5)
    
    t = get_template('profiles/includes/order_list.html')
    html = t.render(RequestContext(request, paging.result(pageNo)))
    
    return HttpResponse(json.dumps({'status': 'success', 'html': html}))
            
def delOrderByProfile(request):
    '''用户在个人订单列表中删除订单, ajax request only'''
    if not request.is_ajax():
        raise Http404
    
    profile = request.user.get_profile()
    
    orderId = request.REQUEST.get('orderId', None)
    if not orderId:
        return HttpResponse(json.dumps({'status': 'failed'}))
    
    try:
        order = Order.objects.get(id=int(orderId))
    except Order.DoesNotExist:
        return HttpResponse(json.dumps({'status': 'failed'}))
    
    if profile == order.owner:
        profile.delOrderIds.append(int(orderId))
        return HttpResponse(json.dumps({'status': 'success'}))
    
    return HttpResponse(json.dumps({'status': 'failed'}))
        
        
        
    
    



