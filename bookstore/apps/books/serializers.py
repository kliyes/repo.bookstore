#coding=utf-8
'''
Created on 2013-7-7

@author: Tom
'''


#the definition of the book model
from rest_framework import serializers
from books.models import Book, Author
from rest_framework.fields import Field
from django.conf import settings
from common.utils import CustomSerializerMethodField, strTime

#class AuthorSerializer(serializers.ModelSerializer):
#    
#    class Meta:
#        model = Author


class BookSerializer(serializers.ModelSerializer):
    
#    author = AuthorSerializer()
    cover = serializers.SerializerMethodField('getCoverPath')
    boughtCount = Field(source='bought_count')
    category = serializers.SlugRelatedField(slug_field='label')
    publishDate = Field(source='publish_date')
    regDate = CustomSerializerMethodField('strTime', 'reg_date')
    commentCount = Field(source='comment_count')
    
    class Meta:
        model = Book
#        fields = ('id', 'name')
        fields = ('id', 'name', 'author', 'price', 'isbn', 'press', 'desc', 'binding', 
            'pages', 'cover', 'boughtCount', 'category', 'stock', 'publishDate', 
            'regDate', 'commentCount')
    
    def getCoverPath(self, obj):
        return settings.MEDIA_URL + 'img/' + obj.mpic
    
    def strTime(self, obj, attr):
        return strTime(getattr(obj, attr))
        
        
        
        
        

