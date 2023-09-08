from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Author, Book, BorrowRequest

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'first_name', 'last_name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BorrowRequestSerializer(serializers.ModelSerializer):
    borrower = UserSerializer(read_only=True)

    class Meta:
        model = BorrowRequest
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def validate_book_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Title length should be at least 3 characters")
        return value

    def validate_book_summary(self, value):
        if not value:
            raise serializers.ValidationError("Summary should not be empty")
        return value


book_data = {
             'title':'Harry Potter',
             'summary':'Fan',
             'isbn':'44556452',
             'available':'True',
             'published_date':'2023-09-03',
             'publisher':'Admin',
             'genres': [2],
             'authors':[3],
             'borrower':1
             }

