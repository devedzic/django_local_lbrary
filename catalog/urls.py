'''
URLconf of the catalog app
'''

from django.urls import path
from . import views


# urlpatterns = [               # this has been just an initial placeholder
#
# ]

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),                   # added as part of the challenge
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),    # added as part of the challenge
]

urlpatterns += [                # added at a later stage, to enable displaying the books borrowed by a specific user
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
]

urlpatterns += [                # added as part of the challenge, to enable displaying all loaned/borrowed books
    path('loaned-books/', views.LoanedBooksListView.as_view(), name='all-borrowed'),
]

urlpatterns += [                # added at a later stage, to enable book renewal through an appropriate form
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
]

