from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Author(models.Model):
    name=models.CharField(max_length=255)
    bio=models.TextField()
     
    def __str__(self):
        return self.name
    

class Genre(models.Model):
    name=models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Book(models.Model):
    title = models.CharField(max_length=255)  
    summary = models.TextField()  
    isbn = models.CharField(max_length=17, unique=True)  # ISBN, unique
    available = models.BooleanField(default=True)  
    published_date = models.DateField()  
    publisher = models.CharField(max_length=255)  
    genres = models.ManyToManyField(Genre, blank=True)  
    authors = models.ManyToManyField(Author)  
    borrower = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.title  
    

# tuple
BORROW_REQUEST_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('COLLECTED', 'Collected'),
    ('COMPLETE', 'Complete'),
    ('DECLINED', 'Declined'),
)

class BorrowRequest(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=BORROW_REQUEST_STATUS_CHOICES, default='PENDING')
    overdue = models.BooleanField(default=False)
    request_date = models.DateField()
    approval_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    complete_date = models.DateField(null=True, blank=True)

    def __str__(self):
         return f"Borrow request for {self.book.title}"
    

