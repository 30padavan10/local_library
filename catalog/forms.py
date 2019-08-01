from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.
    
class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        #Проверка того, что дата не выходит за "нижнюю" границу (не в прошлом). 
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Проверка того, то дата не выходит за "верхнюю" границу (+4 недели).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Помните, что всегда надо возвращать "очищенные" данные.
        return data

# Второй вариант организации формы через ModelForm, можно использовать когда требуется информация только из одной модели. При наличии большого количества полей уменьшает количество кода.

from django.forms import ModelForm
from .models import BookInstance

class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
       data = self.cleaned_data['due_back']
       
       #Проверка того, что дата не в прошлом
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       #Check date is in range librarian allowed to change (+4 weeks)
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Не забывайте всегда возвращать очищенные данные
       return data

    class Meta:
        model = BookInstance
        fields = ['due_back',]    #  можно перечислить поля модели в поле fields которые должны быть включены в форму (вы можете включить все поля при помощи fields = '__all__', или можно вопользоваться полем exclude (вместо fields), чтобы определить поля модели, которые не нужно включать).

        labels = { 'due_back': _('Renewal date'), }  # в этом словаре можно переопределять объявления полей модели (то есть, текстовых меток, виджетов, текстов, сообщений об ошибках).
        help_texts = { 'due_back': _('Enter a date between now and 4 weeks (default 3).'), }
