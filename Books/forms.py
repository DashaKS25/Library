from django import forms
from django.contrib.auth import get_user_model
from Users.models import Book, Genre, Author


UserModel=get_user_model()



class BookForm(forms.ModelForm):
    genres = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), widget=forms.CheckboxSelectMultiple)
    authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Book
        fields = '__all__'

class AuthorForm(forms.ModelForm):
    class Meta:
        model= Author
        fields = ['name', 'bio']

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']