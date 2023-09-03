from django.urls import path
from . import views

app_name = "Users"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('librarian_menu/', views.LibrarianMenuView.as_view(), name='librarian_menu'),
    path('user_office/', views.UserOfficeView.as_view(), name='user_office'),
    path('edit_profile/<int:pk>/', views.EditProfileView.as_view(), name='edit_profile'),
    path('change_passord/', views.ChangePasswordView.as_view(), name='change_password'),
    path('delete_profile/<int:pk>/', views.DeleteUserProfile.as_view(), name='delete_profile')
]
