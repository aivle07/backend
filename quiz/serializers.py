from rest_framework import serializers
from .models import *

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id","question","answer"]
        
class QuizHistorySerializer(serializers.ModelSerializer):
    question = serializers.ReadOnlyField(source = 'quiz_id.question')
    class Meta:
        model = QuizHistory
        fields = ["id","judge","create_dt","question","quiz_id","user_id"]
        
class QuizHistoryRetrieveSerializer(serializers.Serializer):
    quiz = QuizSerializer()
    my_record = QuizHistorySerializer()