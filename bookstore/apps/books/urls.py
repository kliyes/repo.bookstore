from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^getbyname/$", "books.views.getBooksByName", name="book_search"),
    url(r"^(\d+)$", "books.views.bookDetail", name="book_detail"), 
    url(r"^add_to_cart/(\d+)$", "books.views.addToCart", name="book_cart_add"), 
    url(r"^del_from_cart/(\d+)$", "books.views.delFromCart", name="book_cart_del"), 
    url(r"^check_the_cart/$", "books.views.checkCart", name="book_cart_check"), 
    url(r"^make_order/$", "books.views.makeOrder", name="book_order"), 
    url(r"^submit_order/$", "books.views.submitOrder", name="book_order_submit"), 
    url(r"^add_comment/(\d+)$", "books.views.addComment", name="book_add_cmt"), 
    url(r"^mark_book/(\d+)$", "books.views.markBook", name="book_mark"), 
    url(r"^page_books/$", "books.views.pagingBooks"), 
    url(r"^page_cmts/(\d+)$", "books.views.pagingCmts"), 
)