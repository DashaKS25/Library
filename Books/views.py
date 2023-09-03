from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from Users.models import Book, BorrowRequest, Author, Genre
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from .forms  import BookForm, AuthorForm, GenreForm
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.generic import ListView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin

desired_due_date = timezone.now() + timezone.timedelta(days=7)

class BookListView(View):
    template_name = 'book_list.html'

    def get(self, request):
        books = Book.objects.all()
        user_can_edit = request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='admin_librarian').exists())
        return render(request, self.template_name, {'books': books, 'user_can_edit': user_can_edit})

class UpdateBookView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.groups.filter(name='admin_librarian').exists()

    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        form = BookForm(instance=book)
        return render(request, 'update_book.html', {'form': form, 'book': book})

    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('Books:book_list')
        else:
            return render(request, 'update_book.html', {'form': form, 'book': book})

 

class BorrowHistoryView(UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_superuser or user.groups.filter(name='admin_librarian').exists())

    def get(self, request):
        user = request.user
        if user.is_authenticated and user.is_superuser:
            borrow_requests = BorrowRequest.objects.all()
        elif user.is_authenticated:
            borrow_requests = BorrowRequest.objects.filter(borrower=user)
        else:
            error_message = "You don't have permission to access this page."
            return HttpResponse(error_message)
        return render(request, 'borrow_history.html', {'borrow_requests': borrow_requests})
    


class CreateBookView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.groups.filter(name='admin_librarian').exists()

    def get(self, request):
        form = BookForm()
        return render(request, 'create_book.html', {'form': form})

    def post(self, request):
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Books:book_list')
        else:
            return render(request, 'create_book.html', {'form': form})


class ConfirmDeleteBookView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.groups.filter(name='admin_librarian').exists()

    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        return render(request, 'confirm_delete_book.html', {'book': book})

    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        
        if request.POST.get('confirm') == 'Yes':
            book.delete()
            return redirect('Books:book_list')
        else:
            return redirect('Books:book_detail', book.id)   

@login_required
def book_detail(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return HttpResponse("Book not found", status=404)
    
    borrow_request = BorrowRequest.objects.filter(book=book, borrower=request.user).first()

    if request.method == 'POST':
        if 'create_borrow_request' in request.POST:
            borrow_days = request.POST.get('borrow_days')
            if not borrow_days:
                messages.error(request, 'Please provide the number of borrow days.')
            else:
                borrow_days = int(borrow_days)
                due_date = timezone.now() + timedelta(days=borrow_days)
                BorrowRequest.objects.create(
                    book=book,
                    borrower=request.user,
                    status='pending',
                    request_date=datetime.now(),
                    due_date=due_date
                )
                messages.success(request, f'Request for {book.title} sent. Due date: {due_date}')
            return redirect('Books:book_detail', book_id=book.id)
        elif 'collect_book' in request.POST:
            if borrow_request and borrow_request.status == 'approve':
                borrow_request.status = 'completed'
                borrow_request.save()
                book.available = False
                book.save()
                return redirect('Books:book_detail', book_id=book.id)
            
        elif 'return_book' in request.POST:
            if borrow_request and borrow_request.status == 'completed':
                borrow_request.status = 'returned'
                borrow_request.save()
                book.available = True
                book.save()
                return redirect('Books:book_detail', book_id=book.id)
            
    return render(request, 'book_detail.html', {'book': book, 'borrow_request': borrow_request})

class ManageBorrowRequestsView(ListView):
    model = BorrowRequest
    template_name = 'borrow_requests.html'
    context_object_name = 'borrow_requests'

    def get_queryset(self):
        return BorrowRequest.objects.order_by('status', 'request_date')


    def post(self, request):
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        if action == 'approve':
            try:
                borrow_request = BorrowRequest.objects.get(pk=request_id)
                borrow_request.status = 'approve'
                borrow_request.save()
            except BorrowRequest.DoesNotExist:
                raise BorrowRequest.DoesNotExist('This request is not found')
        elif action == 'decline':
            try:
                borrow_request = BorrowRequest.objects.get(pk=request_id)
                borrow_request.status = 'decline'
                borrow_request.save()
            except BorrowRequest.DoesNotExist:
                raise BorrowRequest.DoesNotExist('This request is not found')
        elif action == 'delete':
            try:
                borrow_request = BorrowRequest.objects.get(pk=request_id)
                borrow_request.delete()
            except BorrowRequest.DoesNotExist:
                raise BorrowRequest.DoesNotExist('This request is not found')
        elif action == 'change_availability':
            book_id = request.POST.get('book_id')
            try:
                book = Book.objects.get(pk=book_id)
                book.is_available = not book.is_available
                book.save()
            except Book.DoesNotExist:
                raise Book.DoesNotExist('This book is not found')
        elif action == 'return':
            try:
                borrow_request = BorrowRequest.objects.get(pk=request_id)
                if borrow_request.status == 'returned':
                    book = borrow_request.book
                    book.available = True
                    book.save()
                    borrow_request.delete()
            except BorrowRequest.DoesNotExist:
                raise BorrowRequest.DoesNotExist('This request is not found') 
        


        return redirect(reverse_lazy('Books:borrow_requests'))
    
class SearchResultsView(TemplateView):
    template_name = 'search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        search_results = []

        if query:
            search_results = Book.objects.filter(
                Q(title__icontains=query) | Q(authors__name__icontains=query)
            )

        context['query'] = query
        context['search_results'] = search_results
        return context
    
class AuthorListView(ListView):
    model = Author
    template_name ='author_list.html'
    context_object_name = 'authors'

    def get (self, request):
        authors = Author.objects.all()
        return render(request, self.template_name, {'authors': authors})
    

    
class AuthorsCreate(View):
    template_name= 'author_form.html'
    form_class = AuthorForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('author_list')
        
class GenreListView(ListView):
    template_name = 'genre_list.html'

    def get(self, request):
        genres = Genre.objects.all()
        return render(request, self.template_name, {'genres': genres})

class GenreCreate(View):
    template_name = 'genre_form.html'
    form_class = GenreForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Books:genre_list')
        
class AuthorEditView(View):
    template_name = 'author_edit.html'  

    def get(self, request, pk):
        author = Author.objects.get(pk=pk)
        form = AuthorForm(instance=author)
        return render(request, self.template_name, {'form': form, 'author': author})

    def post(self, request, pk):
        author = Author.objects.get(pk=pk)
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('Books:author_list') 

        return render(request, self.template_name, {'form': form, 'author': author})
    
class GenreEditView(View):
    template_name = 'genre_edit.html'
    form_class = GenreForm

    def get(self, request,pk):
        genre = get_object_or_404(Genre,pk=pk)
        form = self.form_class(instance=genre)
        return render(request, self.template_name, {'form': form, 'genre': genre})

    def post(self, request, pk):
        genre = get_object_or_404(Genre,pk=pk)
        form = self.form_class(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            return redirect('Books:genre_list')
        return render(request, self.template_name, {'form': form, 'genre': genre})
    
class AuthorDeleteView(View):
    template_name = 'author_delete.html'
    
    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        return render(request, self.template_name, {'author': author})
    
    def post(self, request, pk):
        author = get_object_or_404(Author, pk)
        author.delete()
        return redirect('Books:author_list')
    
class GenreDeleteView(View):
    template_name = 'genre_delete.html'
    
    def get(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        return render(request, self.template_name, {'genre': genre})
    
    def post(self, request, pk):
        genre = get_object_or_404(Genre, pk=pk)
        genre.delete()
        return redirect('Books:genre_list')
    


