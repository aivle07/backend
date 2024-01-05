from django.db import models
import os

# Create your models here.
class Report(models.Model):
    title = models.CharField('TITLE', max_length=100)
    file = models.FileField("FILE", upload_to='report/%Y/%m/', blank=True, null=True)
    create_dt = models.DateTimeField('CREATE DT', auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_file_name(self):
        return os.path.basename(self.file.name)
    
    def get_file_path(self):
        return os.path.abspath(self.file.name)