from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^getbyname/$", "books.views.getBooksByName"),
    url(r"^(\d+)$", "books.views.bookDetail", name="book_detail"), 
    url(r"^add_to_cart/(\d+)$", "books.views.addToCart", name="book_cart_add"), 
    url(r"^check_the_cart/$", "books.views.checkCart", name="book_cart_check"), 
    
)