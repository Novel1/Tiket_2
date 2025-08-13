from django.urls import path
from .views import BookListView, rent_book

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('books/<int:book_id>/rent/', rent_book, name='rent_book'),
]