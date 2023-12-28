from django.contrib import admin
from quiz.models import Quiz, QuizHistory

# Register your models here.

admin.site.register(Quiz)
admin.site.register(QuizHistory)