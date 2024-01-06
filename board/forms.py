from django import forms
from board.models import *

class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title","content","image"]