from django import forms
from django.contrib.auth.models import User
from .models import *

class UserSignup(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email' ,'password']

        widgets={
        'password': forms.PasswordInput(),
        }


class UserLogin(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude=['creator']

        widgets={
            'date': forms.DateInput(attrs={'type':"date"}),
            'time': forms.TimeInput(attrs={'type':"time"}),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields=['tickets']




