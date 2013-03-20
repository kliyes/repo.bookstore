from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^getbyname/$", "books.views.getBooksByName"),
    url(r"^(\d+)$", "books.views.bookDetail", name="book_detail"), 
    
)