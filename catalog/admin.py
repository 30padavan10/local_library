from django.contrib import admin


# Register your models here.
# Для более модификации отображения в admin необходимо импортировать модели и затем их нужно зарегистрироавть..
from .models import Genre, Book, Author, BookInstance

#admin.site.register(Book)
#admin.site.register(Author)
admin.site.register(Genre)
#admin.site.register(BookInstance)

class BooksInlineForAuthor(admin.TabularInline):
        model = Book
# позволяет добавить поля встроенной модели BookInstance
        extra = 0



class AuthorAdmin(admin.ModelAdmin):
	#pass
	list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
# list_display - позволяет отображать поля модели вместо, того что возвращает def __str__

	fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] # для отображения полей в нужном порядке, поля объединенные в кортеж, отображаются в одной линии.
	inlines = [BooksInlineForAuthor]	

admin.site.register(Author, AuthorAdmin)  # первый вариант регистрации модели


class BooksInstanceInline(admin.TabularInline):
	model = BookInstance
# позволяет добавить поля встроенной модели BookInstance 
	extra = 0
# позволяет не отображать существующие экземпляры книги

@admin.register(Book)  # второй вариант регистрации модели
class BookAdmin(admin.ModelAdmin):
# мы не можем напрямую поместить поле genre в list_display, так как оно является  ManyToManyField (Django не позволяет это из-за большой "стоимости" доступа к базе данных). Вместо этого мы определим функцию display_genre для получения строкового представления информации

	list_display = ('title', 'author', 'display_genre')
	inlines = [BooksInstanceInline] #при добавлении новой книги на странице редактирования отображает поля втроенной модели класс BooksInstanceInline

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
	

	list_filter = ('status', 'due_back')  # добавляет фильтр 
	list_display = ('id', 'book', 'borrower', 'status', 'due_back')

	fieldsets = (
		(None, {
			'fields': ('book', 'imprint', 'id')
		}),
                ('Availability', {
                        'fields': ('status', 'due_back', 'borrower')
                }),
	)
# fieldsets -  разделение данных на секции, если название секции не нужно, то используется просто None



