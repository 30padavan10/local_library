from django.db import models
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
import uuid # Required for unique book instances
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Genre(models.Model):
	name = models.CharField(max_length=200, help_text='Enter a book genre')

	def __str__(self):
		return self.name

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
# Author as a string rather than object because it hasn't been declared yet in the file.
	summary = models.TextField(max_length=100, help_text='brief description')
	isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
	genre = models.ManyToManyField(Genre, help_text='select genre')
# Genre class has already been defined so we can specify the object above.

	def __str__(self):
       		return self.title

	def get_absolut_url(self):
       		return reverse('book-detail', args=[str(self.id)])

	def display_genre(self):
		"""эта функция собирает [:n] первых жанров книги и создает тесктовую строку, которая будет отображаться в списке книг"""
		return ', '.join([genres.name for genres in self.genre.all()[:2]])

class BookInstance(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID')
	book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
	imprint = models.CharField(max_length=200)
	due_back = models.DateField(null=True, blank=True)
	borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	LOAN_STATUS = (
       		('m', 'Maintenance'),
       		('o', 'On loan'),
       		('a', 'Available'),
       		('r', 'Reserved'),
	)

#Первый элемент каждого кортежа в LOAN_STATUS – это значение, которое будет сохранено в базе данных. Второй элемент – название, которое будет отображаться для пользователей. Можно указать список значений и не в модели, но так все данные будут связаны с моделью, и к значениям можно легко обратиться BookInstance.m

	status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')

	class Meta:
		ordering = ["due_back"]
		permissions = (('can_mark', 'pizza pizza pizza'),)   #Разрешения текущего пользователя будут храниться в переменной шаблона {{ perms }}.  Проверить, имеет ли текущий пользователь определенное разрешение в шаблоне {% if perms.catalog.can_mark_returned %}, или проверить в представлении функции, используя  permission_required декоратор или в представлении на основе классов, используя PermissionRequiredMixin.

#специальный подкласс модели, который позволяет производить сортировку в данной случае, можно также автоматизировать выделение названия таблицы, модель + приложение. Можно менять название таблицы и т.д. 

	def __str__(self):
		return '%s (%s)' % (self.id,self.book.title)

	@property
	def is_overdue(self):
		if self.due_back and date.today() > self.due_back:   # здесь сначала проверяется является ли due_back пустым, чтобы не сравнивать пустые значения
			return True
		return False


class Author(models.Model):
   
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(null=True, blank=True)
	date_of_death = models.DateField('died', null=True, blank=True)
    
	def get_absolut_url(self):
		return reverse('author-detail', args=[str(self.id)])
    

	def __str__(self):
		return '%s, %s' % (self.last_name, self.first_name)

	class Meta:
		permissions = (('Changes_Autho', 'Changes Autho'),)



