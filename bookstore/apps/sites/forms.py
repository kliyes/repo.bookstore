#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import datetime

from django import forms

from common.utils import ecode
from sites.models import Feedback 
from provider.oauth2.models import Client

CONTACT_MAX_LEN = 35
class FeedbackForm(forms.Form):
    contact = forms.CharField(
        max_length=80, 
        required=False,
        widget=forms.TextInput(attrs={"style": "width:450px;"})
    )
    
    content = forms.CharField(
        max_length=500, 
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea-style", "style": "width:450px;height:200px;"}), 
    ) 
    
    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__( *args, **kwargs)
        
    def clean_contact(self):
        value = self.cleaned_data["contact"]
        if len(ecode(value)) > CONTACT_MAX_LEN:
            raise forms.ValidationError(u"联系方式不应超过%s个汉字或%s个英文字符" % (CONTACT_MAX_LEN,CONTACT_MAX_LEN*2))
        return value
    
    def clean_content(self):
        value = self.cleaned_data["content"]
        if len(value) < 8:
            raise forms.ValidationError(u"反馈内容字数不应少于8个")
        if len(value) > 500:
            raise forms.ValidationError(u"反馈内容不应超过500个字")
        return value     

    def save(self, profile):
        feed = Feedback(created_date=datetime.datetime.now())
        feed.contact = self.cleaned_data["contact"].strip()
        feed.content = self.cleaned_data["content"].strip()
        feed.profile = profile
        feed.save()
        return feed


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'url', 'redirect_uri', 'client_type')
