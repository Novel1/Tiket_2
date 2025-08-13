from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Book, Favorite


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'category', 'year', 'price', 'status')
    list_filter = ('category', 'author_name', 'year', 'status')
    search_fields = ('title', 'author_name')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')