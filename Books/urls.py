from django.urls import path
from . import views

app_name = "Books"

urlpatterns = [
    path('book_list/', views.BookListView.as_view(), name='book_list'),
    path('update_book/<int:book_id>/', views.UpdateBookView.as_view(), name='update_book'),
    path('borrow_history/', views.BorrowHistoryView.as_view(), name='borrow_history'),
    path('create_book/', views.CreateBookView.as_view(), name='create_book'),
    path('confirm_delete_book/<int:book_id>/', views.ConfirmDeleteBookView.as_view(), name='confirm_delete_book'),
    path('book_detail/<int:book_id>/', views.book_detail, name='book_detail'),
    path('borrow_requests/', views.ManageBorrowRequestsView.as_view(), name='borrow_requests'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('authors/create/', views.AuthorsCreate.as_view(), name='author_form'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('genres/create/', views.GenreCreate.as_view(), name='genre_create'),
    path('authors/<int:pk>/edit/', views.AuthorEditView.as_view(), name='author_edit'),
    path('genres/<int:pk>/edit/', views.GenreEditView.as_view(), name='genre_edit'),
    path('authors/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author_delete'),
    path('genres/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre_delete'),
   
]
