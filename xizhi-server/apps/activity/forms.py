# -*-coding:utf-8 -*- 
import re
import datetime

from django import forms
from django.conf import settings

from common.utils import ecode
from common.consts import CATEGORY_IT, CATEGORY_STARTUP, CATEGORY_COLLEGE, CATEGORY_OTHER
from activity.models import Activity
from profiles.models import City

alnum_re = re.compile(r"^\w+$")


# @@@ var sample get from settings 
REQUIRED_EMAIL = getattr(settings, "ACCOUNT_REQUIRED_EMAIL", False)

class ActivityForm(forms.Form):
    title = forms.CharField()
    
    category = forms.ChoiceField( #活动分类
        initial='unknown',                    
        choices=(
            (CATEGORY_IT.id, CATEGORY_IT.label), 
            (CATEGORY_STARTUP.id, CATEGORY_STARTUP.label), 
            (CATEGORY_COLLEGE.id, CATEGORY_COLLEGE.label), 
            (CATEGORY_OTHER.id, CATEGORY_OTHER.label),
            )
    ) 
    
    city = forms.CharField()      #举办城市id
    address = forms.CharField(required=False)    #活动详细地址
    startDate = forms.DateField(required=False)   #开始时间
    endDate = forms.DateField(required=False)     #结束时间
    price = forms.FloatField()      #价格, 0表示免费
    desc = forms.CharField(required=False, widget=forms.Textarea(), ) #详细描述
    coordinates = forms.CharField(required=False)
    
    organizer = forms.CharField(required=False)   #主办方
    
    profile = None

    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop("actId", None)
        self.profile = kwargs.pop("profile", None)
        super(ActivityForm, self).__init__(*args, **kwargs)
        
        if self.profile:
            self.fields["city"].initial = self.profile.city.id
        
        if self.id:
            act = Activity.objects.get(id=int(self.id))
            if act:
                self.fields["title"].initial = act.title
                self.fields["desc"].initial = act.content 
    
    def clean_title(self):
        value = self.cleaned_data["title"]
        if not value:
            raise forms.ValidationError(u"Activity title is null ")    
        return value.strip()
    
    def clean_address(self):
        value = self.cleaned_data["address"]
        if value:
            return value.strip()
        raise forms.ValidationError(u"address is null")
    
    def clean_city(self):
        value = self.cleaned_data["city"]
        return value
    
    def clean_desc(self):
        value = self.cleaned_data["desc"]
        if len(ecode(value)) > 800:
            raise forms.ValidationError(u"活动描述不能超过800个汉字或1600个英文字符")
        return value
    
    def clean_price(self):
        return self.cleaned_data["price"]
    
    def clean_startDate(self):
        value = self.cleaned_data["startDate"]
        return value
    
    def clean_endDate(self):
        value = self.cleaned_data["endDate"]    
        return value   
    
    def clean_coordinates(self):
        return self.cleaned_data["coordinates"] 
    
    def clean_organizer(self):
        value = self.cleaned_data["organizer"]
        if not value or len(value.strip()) <= 0:
            return '--'
        if len(ecode(value.strip())) > 50:
            raise forms.ValidationError(u"主办方名称不能超过50个汉字或100个英文字符")
        
        return value.strip()
    
    def clean(self):
        return self.cleaned_data
    
    def save(self, profile):
        act = Activity()
        act.title = self.cleaned_data["title"]
        act.category = self.cleaned_data["category"]
        
        act.city = self.getCity()
        act.address = self.cleaned_data["address"]
        act.start_date = self.cleaned_data["startDate"]
        act.end_date = self.cleaned_data["endDate"]
        act.price = self.cleaned_data["price"]
        act.desc = self.cleaned_data["desc"]
        act.coordinates = self.cleaned_data["coordinates"]
        act.organizer = self.cleaned_data["organizer"] 
        
        act.publisher = profile
        act.published_date = datetime.datetime.now()
        act.last_updated = act.published_date
        act.attendee_count = 0
        act.like_count = 0
        
        act.save()
        return act
    
    def getCity(self):
        cid = self.cleaned_data.get("city")
        if not cid:
            raise forms.ValidationError("city id is null")
        return City.objects.getById(id=int(cid))
        
        
