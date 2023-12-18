from django.shortcuts import render
from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsReviewAuthorOrReadOnly
# Create your views here.

# class BoardViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializers = BoardListSerializerView(queryset)

# 페이지네이션
class BoardPageNumberPagination(PageNumberPagination):
    page_size = 3 # 한페이지당 3개글
    
# 목록보기
class BoardListAPIView(ListAPIView):
    queryset = Post.objects.all().order_by("-id")
    serializer_class = BoardListSerializerView
    pagination_class = BoardPageNumberPagination
    # permission_classes = IsAuthenticatedOrReadOnly
    
    
# 상세보기
class BoardRetrieveAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = BoardDetailSerializerView
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # commentList = instance.comment_set.all().order_by("-id")
        data = {
            "board":instance,
            # "commentList":commentList
        }
        serializer = self.get_serializer(instance=data)
        return Response(serializer.data)
        
# 작성하기
class BoardCreateAPIView(CreateAPIView):
    # authentication_classes = [SessionAuthentication]
    queryset = Post.objects.all()
    serializer_class = BoardCreateSerializerView
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(author = self.request.user)      
        
# 수정하기
class BoardUpdateAPIView(UpdateAPIView):
    # queryset = Post.objects.all()
    serializer_class = BoardUpdateSerializerView
    permission_classes = (IsAuthenticated,)
    
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        instance = self.get_object(pk)
        serializer = BoardUpdateSerializerView(instance)
        return Response(serializer.data)
    
        
    def put(self, request, pk):
        instance = self.get_object(pk)
        serializer = BoardUpdateSerializerView(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 삭제하기
class BoardDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = BoardDeleteSerializerView
    permission_classes = (IsAuthenticated,)
