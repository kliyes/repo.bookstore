#coding=utf-8
'''
Created on 2013-7-7

@author: Tom
'''
from rest_framework import generics, status
from books.serializers import BookSerializer, BasicBookSerializer
from books.models import Book
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class BookList(generics.ListAPIView):
    '''list all the books'''
    
    model = Book
#     serializer_class = BookSerializer
    serializer_class = BasicBookSerializer
    
class BookDetail(GenericAPIView):
    '''detail of a book'''
    
    def get(self, request):
        
        bookId = request.GET.get('bookId')
        try:
            book = Book.objects.get(id=int(bookId))
        except Book.DoesNotExist:
            return Response({'errMsg': u'指定书籍不存在', 'errCode': 'EC_0404'}, 
                status=status.HTTP_404_NOT_FOUND)
            
        serializer = BookSerializer(book)
        return Response(serializer.data)
        
            