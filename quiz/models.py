from django.db import models
from accounts.models import User

class Quiz(models.Model):
    question = models.TextField('QUESTION')
    answer = models.CharField('ANSWER', max_length=3)

    def __str__(self):
        return self.question
    
class QuizHistory(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    judge = models.CharField(max_length=3)
    create_dt = models.DateField(auto_now_add=True)
    
    