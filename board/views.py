from collections import OrderedDict
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import AllowAny
from .permissions import IsAuthorOrReadOnly
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer,BrowsableAPIRenderer
from django.core.paginator import Paginator

# Create your views here.

# class BoardViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializers = BoardListSerializerView(queryset)

from django.shortcuts import render
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# # 페이지네이션
# class BoardPageNumberPagination(PageNumberPagination):
#     page_size = 3 # 한페이지당 3개글
#     page_size_query_param = 'page_size'
    
# 목록보기
class BoardListAPIView(ListAPIView):
    queryset = Post.objects.all().order_by("-id")
    serializer_class = BoardListSerializerView
    
    def list(self, request):
        notice_instance = Paginator(Post.objects.filter(category='공지사항').order_by("-id"), 3)
        notice_page = int(request.GET.get('notice_page',1))
        notice_list = notice_instance.get_page(notice_page)
        
        qna_instance = Paginator(Post.objects.filter(category='Q&A').order_by("-id"), 3)
        qna_page = int(request.GET.get('qna_page',1))
        qna_list = qna_instance.get_page(qna_page)
        
        
        return render(request,context={'notice': notice_list,'qna': qna_list}, template_name='board/notice.html',)
        
    #     #category = request.GET.get('category',None)
    #     notice_instance = Post.objects.filter(category='공지사항').order_by("-id")
    #     qna_instance = Post.objects.filter(category='Q&A').order_by("-id")
            
    #     notice_qs = self.filter_queryset(notice_instance)
    #     qna_qs = self.filter_queryset(qna_instance)

    #     notice_page = self.paginate_queryset(notice_qs)
    #     qna_page = self.paginate_queryset(qna_qs)
    #     notice_serializer = self.get_serializer(notice_page, many=True)
    #     qna_serializer = self.get_serializer(qna_page, many=True)
    #     notice = self.get_paginated_response(notice_serializer.data)
    #     qna = self.get_paginated_response(qna_serializer.data)
    #     print(notice.data,qna.data)
    #     return Response({'notice': notice.data, 'qna':qna.data}, template_name='board/notice.html',)

    
    
# 상세보기 -완-
class BoardRetrieveAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = BoardDetailSerializerView
    #permission_classes = (IsAuthorOrReadOnly,)
    
    def retrieve(self, request, pk):
        
        instance = Post.objects.filter(id=pk).first()
        commentList = instance.comment_set.all().order_by("-id")
        data = {
            "board":instance,
            "commentList":commentList
        }
        # if not request.user.is_admin:
        #     self.check_object_permissions(request, instance) # 이것을 qna에 이용
        serializer = self.get_serializer(instance=data)
        return render(request,"board/notice_contents.html",{'data' :serializer.data})
    
    def get(self, request, pk):
        category = Post.objects.filter(id=pk).first().category
        if category != "qna":
            self.permission_classes = (AllowAny,)
        return self.retrieve(request, pk)
    
        
# 작성하기 -완-
class BoardCreateAPIView(CreateAPIView):
    # authentication_classes = [SessionAuthentication]
    queryset = Post.objects.all()
    serializer_class = BoardCreateSerializerView
    #permission_classes = (IsAuthenticated,IsAuthorOrReadOnly)
    
    def get(self, request):
        return render(request,'board/notice_write.html')

    def perform_create(self, serializer):
        serializer.save(author = self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return redirect(reverse("board:board-list"))
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response   
        
# 수정하기
class BoardUpdateAPIView(UpdateAPIView):
    # queryset = Post.objects.all()
    serializer_class = BoardUpdateSerializerView
    permission_classes = (IsAuthorOrReadOnly,IsAuthenticated)
    
    def get_object(self,pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        instance = self.get_object(pk)
        self.check_object_permissions(request, instance) # 이것을 qna에 이용
        serializer = BoardUpdateSerializerView(instance)
        return render(request,'board/notice_write.html',{'data':serializer.data})
    
        
    def put(self, request, board, pk):
        
        instance = self.get_object(board, pk)
        serializer = BoardUpdateSerializerView(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 삭제하기
class BoardDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = BoardDeleteSerializerView
    permission_classes = (IsAuthorOrReadOnly,IsAuthenticated)

@api_view(('POST', 'GET'))
def board_update(request,pk):
    post = get_object_or_404(Post,id=pk)
    if request.method == "POST":
        # 수정
        form = PostModelForm(request.POST,request.FILES,instance=post)
        if form.is_valid():
            form.save()
        return redirect(post)
    else:
        serializer = BoardUpdateSerializerView(post)
    return render(request, 
                  template_name="board/notice_write.html",
                  context={"data":serializer.data},)
   
# 삭제 
def board_delete(request,category,pk):
    post = get_object_or_404(Post,id=pk)
    post.delete()
    return redirect("board:board-list")