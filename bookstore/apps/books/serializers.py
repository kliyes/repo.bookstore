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

class AuthorSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = Author
#         fields = ('id', 'name')


class BookSerializer(serializers.ModelSerializer):
    
    author = AuthorSerializer()
    cover = serializers.SerializerMethodField('getCoverPath')
    boughtCount = Field(source='bought_count')
    category = serializers.SlugRelatedField(slug_field='label')
    publishDate = Field(source='publish_date')
    #regDate = serializers.SerializerMethodField('strRegDate')
    regDate = Field(source='reg_date')
    commentCount = Field(source='comment_count')
    
    class Meta:
        model = Book
        fields = ('id', 'name', 'author', 'price', 'isbn', 'press', 'desc', 'binding', 
            'pages', 'cover', 'boughtCount', 'category', 'stock', 'publishDate', 
            'regDate', 'commentCount')
#         depth = 1  # 指定关联对象显示的深度
        
    def getCoverPath(self, obj):
        return settings.MEDIA_URL + 'img/' + obj.mpic
     
    def strRegDate(self, obj):
        return obj.reg_date.strftime('%Y-%m-%d %H:%M:%S')
        
class BasicBookSerializer(BookSerializer):
    
    class Meta:
        model = Book
        fields = ('id', 'name', 'cover')       
        
        

