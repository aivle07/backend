from rest_framework import serializers
from .models import *

# 목록보기
class BoardListSerializerView(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')
    class Meta:
        model = Post
        fields = ["id","title","author","create_dt"]
  
# 세부 글      
class BoardRetrieveSerializerView(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')
    class Meta:
        model = Post
        fields = ["id","title","content","category","image","author","create_dt"]
        
# qna 댓글
class CommentSerializerSub(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id","content","create_dt"]
        
# 세부 글 serializer
class BoardDetailSerializerView(serializers.Serializer):
    board = BoardRetrieveSerializerView()
    commentList = CommentSerializerSub(many=True)
    
# 글 작성 (리다이렉트 추가)
class BoardCreateSerializerView(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')
    class Meta:
        model = Post
        fields = ["title","content","image","category","author","create_dt"]
        
# 글 수정
class BoardUpdateSerializerView(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')
    class Meta:
        model = Post
        fields = ["title","content","image","author"]
        
# 글 삭제
class BoardDeleteSerializerView(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        