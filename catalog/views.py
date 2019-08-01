from django.shortcuts import render
from django.views import generic

# Create your views here.

from .models import Book, Author, BookInstance, Genre
from  django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


def index(request):
	"""
	Функция отображения для домашней страницы сайта.
	"""
	# Генерация "количеств" некоторых главных объектов
	num_books=Book.objects.all().count()
	num_instances=BookInstance.objects.all().count()
	# Доступные книги (статус = 'a')
	num_instances_available=BookInstance.objects.filter(status__exact='a').count()
	num_authors=Author.objects.count()  # Метод 'all()' применен по умолчанию.
    
	# Number of visits to this view, as counted in the session variable.
	num_visits=request.session.get('num_visits', 0)
	request.session['num_visits']= num_visits+1

	# Отрисовка HTML-шаблона index.html с данными внутри 
	# переменной контекста context
	return render(
		request,
		'index.html',
		context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors, 'num_visits':num_visits},
	)

class BookListView(generic.ListView):
	model = Book
# отображение выполнит запрос к базе данных, получит все записи заданной модели (Book), затем отрендерит соответствующий шаблон, расположенный в /locallibrary/catalog/templates/catalog/the_model_name_list.html


	context_object_name = 'my_book_list'   # ваше собственное имя переменной контекста в шаблоне
	queryset = Book.objects.filter(title__icontains='а') # Получение 5 книг, содержащих слово 'war' в заголовке
	template_name = 'catalog/book_list.html'  # Определение имени вашего шаблона и его расположения


# можно переопределять методы получения данных. Данный метод заменяет queryset, он более гибкий, но в данном примере разницы нет
#	def get_queryset(self):
#		return Book.objects.filter(title__icontains='war')[:5]

	paginate_by = 10 # при наличии более 10 записей в базе, на страницу будет выводиться только 10, остальные записи будут на следующих страницах. Для возможности переключения между страницами необходимо добавить настройки в шаблон.

	def get_context_data(self, **kwargs):
		# В первую очередь получаем базовую реализацию контекста
		context = super(BookListView, self).get_context_data(**kwargs)
		# Добавляем новую переменную к контексту и иниуиализируем ее некоторым значением
		context['some_data'] = 'This is just some data'
		return context

# данный метод позволяет например в общем представлении detail добавить связную информацию в виде списка. Например если у нас detailview показывает издателя, то с помощью get_context_data можно также отобразить спикок книг этого издателя.


class AuthorListView(generic.ListView):
	model = Author
	context_object_name = 'author_list'
	queryset = Author.objects.all()
	template_name = 'catalog/author_list.html'
	paginate_by = 3


class BookDetailView(generic.DetailView):
	model = Book

class AuthorDetailView(generic.DetailView):
	model = Author


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
	"""
	представление для получения списка всех книг, которые были предоставлены текущему пользователю.
	"""

	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
# переопределяем queryset, чтобы отображать список только конкретного пользователя.


class AllBorrowedBookListView(PermissionRequiredMixin, generic.ListView):
	model = BookInstance
	template_name = 'catalog/bookinstance_list_all_borrowed_workers.html'
	paginate_by = 10
	permission_required = 'catalog.can_mark'
	context_object_name = 'all_borrowed'

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')


from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark')
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


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.Changes_Autho'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.Changes_Autho'

    
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors') # для перехода на страницу списка авторов после удаления одного из них — reverse_lazy() это более "ленивая" версия reverse(). Используется потому что Джанго не знает, что выполнять после удаления записи из таблицы.

# шаблоны для представлений "создать" и "обновить" должны быть с именем model_name_form.html, по умолчанию: (вы можете поменять суффикс на что-нибудь другое, при помощи поля template_name_suffix

# Отображение "удалить" ожидает шаблон с именем формата model_name_confirm_delete.html
    permission_required = 'catalog.Changes_Autho'





















