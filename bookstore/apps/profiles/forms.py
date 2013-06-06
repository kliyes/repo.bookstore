#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import re

from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from profiles.models import Profile
from profiles.signals import profileUpdated
from common.utils import ecode

alnum_re = re.compile(r"^\w+$")

class SimpleRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    '''
    rewrite the default render method, to output widgets without <ul> or <li> tags.
    '''
    
    def render(self):
        """Outputs widget without <ul> or <li> tags."""
        return mark_safe(u'\n'.join([u'%s%s' % 
            (w.tag(), force_unicode(w.choice_label)) for w in self]))
        
class ProfileForm(forms.Form):
    name = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput()
    )
    desc = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(), 
    )
    addr = forms.CharField(
        required=False, 
        max_length=300, 
        widget=forms.TextInput()
    )
    contact = forms.CharField(
        required=False, 
        max_length=30, 
        widget=forms.TextInput()
    )
    receiver = forms.CharField(
        required=False, 
        max_length=10, 
        widget=forms.TextInput()
    )
    
    
#    website = forms.CharField(
#        required = False,                          
#        max_length = 50,
#        widget=forms.TextInput()
#    )
    
#    spacename = forms.CharField(
#        required = False,
#        max_length = 50,
#        widget=forms.TextInput()
#    )
    
    # location choices
    #city = forms.CharField()
    
    #cityName = None
    #cityName = forms.CharField()
    
    sex = forms.ChoiceField(
       required=False,
       initial='unknown',                    
       choices=(('male', u"男"), ('female', u'女'), ('unknown', u"保密")),
       widget=forms.RadioSelect(renderer=SimpleRadioFieldRenderer),
    )  
    
    email = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput()
   )
    
    user = None
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        draftProfile = kwargs.pop("draftProfile", None)
        
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # 优先以当前登录用户profile初始化profile form. 后续逻辑以draftProfile进行覆盖
        if self.user:
            p = self.user.get_profile()
            if not p:
                raise Profile.DoesNotExist
            
            self.fields["name"].initial = p.name
            #self.fields["sex"].initial = p.sex
            self.fields["desc"].initial = p.desc
            self.fields['contact'].initial = p.contact
            self.fields['addr'].initial = p.addr
            self.fields['receiver'].initial = p.receiver
            #self.fields["email"].initial = p.user.email
            
        # 如果之前进入过setup页面，且用户已输入数据，则从session中取得输入数据草稿
        # 该session中的值由之前请求中的save_profile函数设定
        if draftProfile:
            self.fields["name"].initial = draftProfile.name
            self.fields["desc"].initial = draftProfile.desc
            self.fields['contact'].initial = draftProfile.contact
            self.fields['addr'].initial = draftProfile.addr
            self.fields['receiver'].initial = draftProfile.receiver
            #self.fields["sex"].initial = draftProfile.sex
            
    def clean_name(self):
        #other code later
        value = self.cleaned_data.get("name")
        if len(ecode(value)) > 16 or len(ecode(value)) <= 0:
            raise forms.ValidationError(u"昵称不能为空或者多于8个汉字(或16个英文字符)")
        return value
    
#    def clean_city(self):
#        return self.cleaned_data.get("city")
    
    def clean_sex(self):
        return self.cleaned_data.get("sex")
    
#    def clean_website(self):
#        website = self.cleaned_data.get("website", None)
#        nowWebsite = Profile.objects.get(id=self.user.get_profile().id).website
#        if nowWebsite and nowWebsite != website:
#            raise forms.ValidationError(u"个性域名已设置，不可修改")
#        if not website:
#            return website.strip().lower()
#        if website.isdigit():
#            raise forms.ValidationError(u"个性域名不能全为数字")
#        if website and len(website.strip()) < 3:
#            raise forms.ValidationError(u"个性域名不应少于3个英文字符")
#        if len(website.strip()) > 20:
#            raise forms.ValidationError(u"字数应限制在20个英文字符以内")
#        
#        try:
#            pro = Profile.objects.get(website__iexact=website)
#            
#            # 当前用户自身原有的web site
#            if pro.id == self.user.get_profile().id:
#                return pro.website
#            
#            raise forms.ValidationError(u"个性域名已被使用,请重新设定")
#        except Profile.DoesNotExist:
#            return website.strip().lower()
#        
#    def clean_spacename(self):
#        spacename = self.cleaned_data.get("spacename", None)
#        if not spacename or len(spacename.strip()) <= 0:
#            return self.user.get_profile().name
#        if len(ecode(spacename.strip())) > 16:
#            raise forms.ValidationError(u"主页名称不能多于8个汉字(或16个英文字符)")
#        
#        return spacename.strip()
             
    def clean_desc(self):
        value = self.cleaned_data.get("desc")
        if len(ecode(value)) > 400:
            raise forms.ValidationError(u"个人简介字数应限制在200汉字(或400英文字符)以内")
        return value
    
    def clean(self):
        return self.cleaned_data
    
    def save(self, request):
        profile = Profile.objects.get(user=request.user)
        if profile is None:
            profile = Profile(user=request.user)
            
        profile.name = self.cleaned_data.get("name")
        profile.sex = self.cleaned_data.get("sex")
        profile.contact = self.cleaned_data.get("contact")
        profile.addr = self.cleaned_data.get("addr")
        profile.receiver = self.cleaned_data.get("receiver")
        #profile.city = self.getCity()
        #profile.website = self.cleaned_data.get("website")
        #profile.spacename = self.cleaned_data.get("spacename")
        profile.desc = self.cleaned_data.get("desc")
        profile.save()
        
        profileUpdated.send(sender=profile.__class__, request=request, profile=profile) 
        
        return profile
                
#    def getCity(self):
#        cid = self.cleaned_data.get("city")
#        if cid is None:
#            raise forms.ValidationError("city id is null")
#        return City.objects.getById(id=int(cid)) 
        
class PictureForm(forms.Form):
    pic = forms.ImageField(
        label = u"大头像",
        widget = forms.FileInput(attrs={"id": "upload-tx", }),
        error_messages={'required': u"还没有选中任何图片"}
    )
        
