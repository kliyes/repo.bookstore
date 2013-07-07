'''
Created on 2013-7-7

@author: Tom
'''


#the definition of the book model
from rest_framework import serializers
from books.models import Book




class BookSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Book
        