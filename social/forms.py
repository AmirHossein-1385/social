from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import message

from .models import *


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    repeat_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone','password', 'repeat_password')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')
        if password != repeat_password:
            raise forms.ValidationError("پسورد ها مطابقت ندارند")

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("phone already exists!")
        return phone


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name','last_name','email', 'phone', 'date_of_birth', 'bio', 'photo', 'job')


    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.exclude(id =self.instance.id).filter(phone=phone).exists():
            raise forms.ValidationError("phone already exists!")
        return phone


    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id =self.instance.id).filter(username=username).exists():
            raise forms.ValidationError("username already exists!")
        return username


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['name','message','phone','subject','email']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("شماره تلفن عددی نیست")
            else:
                return phone



class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description','tags','image']


class SearchForm(forms.Form):
    query = forms.CharField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name','body']

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description','tags']
