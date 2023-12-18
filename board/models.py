from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField('Category', max_length=50)
    title = models.CharField('TITLE', max_length=50)
    image = models.ImageField('IMAGE', upload_to='board/%Y/%m/', blank=True, null=True)
    content = models.TextField('CONTENT')

    def __str__(self):
        return self.title