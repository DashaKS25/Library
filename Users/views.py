from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import RegistrationForm, EditProfileForm
from django.contrib.auth import get_user_model
from django.views.generic import ListView, View, TemplateView, UpdateView, DeleteView, FormView
from .models import Book, BorrowRequest , Author
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.contrib import messages
from rest_framework import viewsets, status 
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import AuthorSerializer, BookSerializer



UserModel = get_user_model()

class LoginView(LoginView):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid credentials. Please try again."
            return render(request, self.template_name, {'error_message': error_message})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class RegistrationView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = '/home/'  

    def form_valid(self, form):
        username = form.cleaned_data['username']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        password = form.cleaned_data['password']

        if UserModel.objects.filter(username=username).exists():
            error_message = "Username is already used."
            return render(self.request, self.template_name, {'form': form, 'error_message': error_message})

        if password != form.cleaned_data['confirm_password']:
            error_message = "Passwords do not match."
            return render(self.request, self.template_name, {'form': form, 'error_message': error_message})

        user = UserModel(username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

        success_message = "Registration successful! You can now log in."
        return render(self.request, self.template_name, {'success_message': success_message})

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

class LibrarianMenuView(View):
    def get(self, request):
        return render(request, 'librarian_menu.html')

class UserOfficeView(LoginRequiredMixin, View):
    template_name = 'user_office.html'
    login_url = '/login/'


    def get(self, request):
        user = request.user
        borrowed_books_count = BorrowRequest.objects.filter(borrower=user, status='approved').count()
        context = {
            'user': user,
            'borrowed_books_count': borrowed_books_count,
        }
        return render(request, self.template_name, context)
    
class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = EditProfileForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('Users:user_office')
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        return self.request.user

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('user_office')

class DeleteUserProfile(DeleteView):
    model = UserModel
    template_name = 'delete_profile.html'
    success_url = reverse_lazy('user_office')
    pk_url_kwarg = 'pk'


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    @action(detail=True, methods=(['get']))
    def books (self, request, pk=None):
        author = self.get_object()
        book_name = request.query_params.get('book_name', '')
        books = author.books.filter(title__icontains=book_name)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def filter_by_author_age(self, request):
        author_age = request.query_params.get('author_age', '')
        if author_age.isdigit():
            books = Book.objects.filter(authors__bio__icontains=f'age: {author_age}')
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)
        return Response([])

    def create(self, request, *args, **kwargs):
        request.data['title'] += '!'
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
