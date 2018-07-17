from django.db import models
from django.urls import reverse     # used to generate URLs by reversing the URL patterns
import uuid                         # required for unique book instances
from django.contrib.auth.models import User     # added at a later stage, to enable users to borrow books from the lib
from datetime import date                       # added at a later stage, to enable users to borrow books from the lib

# Create your models here.


class Genre(models.Model):
    """
    Model representing a book genre (e.g. Science Fiction, Non Fiction).
    """
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file.

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13,
                            # Me: 'ISBN' is the optional 'verbose_name' first positional argument,
                            # see https://docs.djangoproject.com/en/2.0/topics/db/models/#verbose-field-names
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.title

    def get_absolute_url(self):     # necessary if specific Book pages in admin should include "View on site" button
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    display_genre.short_description = 'Genre'   # short_description is the attribute of display_genre(), defined right here
    # In Python it's not necessary to declare attributes of an object in advance.
    # It's perfectly normal to add arbitrary attributes to an object whenever you like.
    # In this case, display_genre is not a pre-defined attribute of model.Model.
    # It is an extra attribute of the method display_genre, defined ad-hoc,
    # but Python's admin app will use it if it is found.
    # But it is important to use exactly the short_description identifier for that attribute (nothing else works).
    # Thet's because when using a callable, a model method, or a ModelAdmin method to customize a column’s title,
    # you can do it by adding a short_description attribute to the callable
    # (see Django docs,
    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display,
    # the first bullet point after "Here’s a full example model").
    # See also:
    # https://stackoverflow.com/questions/26089942/in-django-where-are-defined-the-attributes-short-description-boolean-and-admin,
    # it implicitly follows from there that short_description, boolean and admin_order_field must be used as is.

class BookInstance(models.Model):
    """
    Model representing a specific copy of a book (i.e. that can be borrowed from the library).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    # Read https://docs.djangoproject.com/en/2.0/ref/models/fields/#uuidfield, it's important!

    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')
    # See choices=LOAN_STATUS - it's very important! It lets users select a value (choice) from a combo box.
    # The value in a key/value pair is a display value that a user can select,
    # while the keys are the values that are actually saved if the option is selected.
    # Also a default value of 'm' (maintenance) is set, as books will initially be created unavailable
    # before they are stocked on the shelves.

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # added at a later stage, to enable users to borrow books from the lib

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            # self.due_back and date.today():
            # We first verify whether due_back is empty (None) before making a comparison.
            # An empty due_back field would cause Django to throw an error instead of showing the page:
            # empty values are not comparable.
            return True
        return False
    # added at a later stage, to enable users to borrow books from the lib

    @property                           # added at a later stage, as part of the challenge
    def is_on_loan(self):
        if self.status == 'o':
            return True
        return False


    class Meta:
        ordering = ["due_back"]         # the default ordering of records returned when you query the model type
        permissions = (("can_mark_returned", "Set book as returned"),)  # added at a later stage (for librarians)

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1})'.format(self.id, self.book.title)     # alternatively: return f'{self.id} ({self.book.title})'
        #  Remember this trick with formatted strings (especially the Python 3.6 f'...' notation), it can be useful!
        #  See https://docs.python.org/3/reference/lexical_analysis.html#f-strings for a more general explanation.

    # def display_due_date(self):                                 # you added this, in response to the challenge
    #     return self.due_back
    # display_due_date.short_description = 'To be returned'

    # You added the above method and its short_description originally, in response to the challenge,
    # but then realized that defining a method like display_due_date() in models.py
    # makes sense only if the corresponding field is a ManyToManyField field (and due_back is not).


class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    # date_of_death = models.DateField('Died', null=True, blank=True)   # changed 'Died' to 'died'
    # Label definition should follow Django's convention of not capitalising the first letter of the label
    # (Django does this for you).
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]  # the default ordering of records returned when you query the model type

    def get_absolute_url(self):     # necessary if specific Author pages in admin should include "View on site" button
        """
        Returns the url to access a particular author instance.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return '{0}, {1}'.format(self.last_name, self.first_name)


class Language(models.Model):
    """
    Model representing a Language (e.g. English, French, Japanese, etc.)
    """
    name = models.CharField(max_length=200,
                            help_text="Enter a the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

