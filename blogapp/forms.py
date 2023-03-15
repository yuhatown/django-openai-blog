from django import forms
from .models import Blog, Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class CreateBlog(forms.ModelForm):
    class Meta:
        model = Blog
 
        fields = ['title', 'category', 'body', 'tag']

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width: 100%', 'placeholder': '제목을 입력하세요.'}
            ),
            'category': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width: 100%'}
            ),
            'body': forms.CharField(widget=CKEditorUploadingWidget()),
            'tag': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width: 100%'}
            ),
        }

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
 
        fields = ['comment_textfield']
        widgets = {
            'comment_textfield': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 40})
        }