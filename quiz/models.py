from django.db import models

class Quiz(models.Model):
    question = models.TextField('QUESTION')
    answer = models.CharField('ANSWER', max_length=3)

    def __str__(self):
        return self.question