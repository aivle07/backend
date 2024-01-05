from django.db import models
from django.urls import reverse
from accounts.models import User
import os


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField('Category', max_length=50)
    title = models.CharField('TITLE', max_length=50)
    image = models.ImageField('IMAGE', upload_to='board/%Y/%m/', blank=True, null=True)
    content = models.TextField('CONTENT')
    create_dt = models.DateTimeField('CREATE DT', auto_now_add=True, null=True)

    def __str__(self):
        return self.title
    
    def get_file_name(self):
        return os.path.basename(self.image.name)
    
    def get_absolute_url(self):
        return reverse("board:board-list")
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField('CONTENT')
    create_dt = models.DateTimeField('CREATE DT', auto_now_add=True)
    update_dt = models.DateTimeField('UPDATE DT', auto_now=True)

    @property
    def short_content(self):
        return self.content[:10]

    def __str__(self):
        return self.short_content