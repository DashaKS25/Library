from django.contrib import admin

from .models import Author, Genre, Book, BorrowRequest

# here models for admin 
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(BorrowRequest)
