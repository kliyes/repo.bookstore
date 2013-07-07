'''
Created on 2013-7-7

@author: Tom
'''
from rest_framework import generics
from books.serializers import BookSerializer
from books.models import Book

class BookList(generics.ListAPIView):
    '''list all the books'''
    model = Book
    serializer_class = BookSerializer
    
class BookDetail(generics.RetrieveAPIView):
    '''detail of a book'''
    model = Book
    serializer_class = BookSerializer