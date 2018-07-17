from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language

# Register your models here.


# admin.site.register(Book)             # used initially, commented out later in favor of the BookAdmin class
# admin.site.register(Author)           # used initially, commented out later in favor of the AuthorAdmin class
admin.site.register(Genre)
# admin.site.register(BookInstance)     # used initially, commented out later in favor of the BookInstanceAdmin class
admin.site.register(Language)

# Enable inline editing of Book objects as associated to Author objects
# class BooksInline(admin.TabularInline):     # StackedInline: vertical layout (like the default model layout)
class BooksInline(admin.TabularInline):     # TabularInline: horizontal layout, more compact
    model = Book
    extra = 0                               # show no extra (empty) BookInstance items with a Book item

# Define the AuthorAdmin class in order to be able to customize the admin interface
class AuthorAdmin(admin.ModelAdmin):
    # pass                                # initially it was just that
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    # this is OK, since all 4 fields are CharField or DateField fields in Author
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]

# Register the AuthorAdmin class with the associated model
admin.site.register(Author, AuthorAdmin)

# Enable inline editing of BookInstance objects as associated to Book objects
# class BooksInstanceInline(admin.TabularInline):     # StackedInline: vertical layout (like the default model layout)
class BooksInstanceInline(admin.TabularInline):     # TabularInline: horizontal layout, more compact
    model = BookInstance
    extra = 0                                       # show no extra (empty) BookInstance items with a Book item

# Register the BookAdmin class using the corresponding decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # pass                                # initially it was just that
    list_display = ('title', 'author', 'display_genre')
    # author is a ForeignKey field in Book, so it's OK;
    # genre is a ManyToManyField field in Book, so an "intermediary" - display_genre - is required by Django
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # pass                                # initially it was just that
    list_filter = ('status', 'due_back')
    # list_display = ('status', 'id', 'book', 'display_due_date')
    # You added this originally, in response to the challenge,
    # but then realized that defining a method like display_due_date() in models.py
    # makes sense only if the corresponding field is a ManyToManyField field (and due_back is not).
    # So, in the end, you added the line below.
    list_display = ('status', 'id', 'book', 'due_back', 'borrower')     # you added this, in response to the challenge
                                                                        # 'borrower' has been added subsequently

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')                # 'borrower' has been added subsequently
        }),
    )


