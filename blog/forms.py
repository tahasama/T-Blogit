from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Comment, Post
from ckeditor.widgets import CKEditorWidget

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class UserCreationEmailForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    def clean(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already exists! try another one.')
        username=self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists! try another one.')

    class Meta:
        model = User
        fields = ('username','email','first_name','last_name',)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email')

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=50, required=True)
    name = forms.CharField(max_length=20, required=True)
    from_email = forms.EmailField(max_length=50, required=True)
    message = forms.CharField(max_length=500,widget=forms.Textarea(),help_text='Write here your message!')

class CommentForm(forms.ModelForm):
    content = forms.CharField(max_length=500,widget=forms.Textarea()) # to cancel CKeditor
    #content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Comment
        fields = ('content',)
    
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('category','title','introduction','body','tags')


class SearchForm(forms.Form):
    query = forms.CharField(label=False,widget=forms.TextInput(attrs=dict(placeholder=(" hit enter to search"))))