from django.shortcuts import render
from django.views import generic                                # added at a later stage
from django.contrib.auth.mixins import LoginRequiredMixin       # added at a later stage
from django.contrib.auth.mixins import PermissionRequiredMixin  # added at a later stage, as part of the challenge

from django.shortcuts import get_object_or_404                  # added at a later stage
from django.http import HttpResponseRedirect                    # added at a later stage
from django.urls import reverse                                 # added at a later stage
import datetime                                                 # added at a later stage

from django.contrib.auth.decorators import permission_required  # added at a later stage

# Create your views here.

from .models import Book, Author, BookInstance, Genre           # added at a later stage
from .forms import RenewBookForm                                # added at a later stage


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable. Added subsequently.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Added as part of the challenge
    num_genres = Genre.objects.count()
    num_books_devotion = Book.objects.filter(title__contains='Devotion').count()

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books': num_books,
                 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,
                 'num_genres': num_genres,                      # added as part of the challenge
                 'num_books_devotion': num_books_devotion,      # added as part of the challenge
                 'num_visits': num_visits},                     # added subsequently
    )

class BookListView(generic.ListView):
    model = Book
    # paginate_by = 10      # added at a later stage, to enable pagination
    paginate_by = 2         # set to 2 to see the actual effects of pagination

    # Possible extensions: see the end of
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#View_(class-based)

    def get_queryset(self):     # overriding ListView.get_queryset(); this is typically done
        # return Book.objects.filter(title__icontains='rock')[:5]  # get 5 books containing 'rock' in the title
        return Book.objects.all()   # get all books, for testing purposes

class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):         # added as part of the challenge
    model = Author
    paginate_by = 2                             # set to 2 to see the actual effects of pagination

    def get_queryset(self):                     # overriding ListView.get_queryset(); this is typically done
        return Author.objects.all()             # get all books, for testing purposes


class AuthorDetailView(generic.DetailView):     # added as part of the challenge
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 2
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


from django.views.generic.edit import CreateView, UpdateView, DeleteView    # added subsequently
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):                                             # added subsequently
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    # reverse_lazy() used here instead of reverse() because we're providing a URL to a class-based view attribute


class BookCreate(CreateView):                                             # added as part of the challenge
    model = Book
    fields = '__all__'
    initial={'language':'English',}

class BookUpdate(UpdateView):
    model = Book
    fields = ['title','author','summary','genre', 'language']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    # reverse_lazy() used here instead of reverse() because we're providing a URL to a class-based view attribute


