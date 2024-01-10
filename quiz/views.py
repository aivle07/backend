from django.shortcuts import render
from django.db.models import Max
from rest_framework.response import Response
import random
from .serializers import *
from .models import *
from .permissons import *
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer,BrowsableAPIRenderer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from datetime import datetime
from django.contrib.auth.decorators import login_required 
from rest_framework.decorators import api_view, renderer_classes
# Create your views here.


# 1. 랜덤 리스트 뽑는다.
# 2. 히스토리db를 본다.
# request.user, 오늘 날짜 같은 것 중에서 quiz_id를 뽑고 리스트로 만든다.
 
# quiz_id가 겹치는 것이 있다면
#   -> continue


def get_random(request):
    cached_result = cache.get('random_quiz')
    
    if cached_result is not None:
        # 캐시에 값이 존재하면 그 값을 반환합니다.
        return cached_result
    
    max_id = Quiz.objects.all().aggregate(max_id=Max("id"))['max_id']
    # 히스토리 db가져오기
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    quiz_history = QuizHistory.objects.filter(user_id=request.user, create_dt=now_date)
        
    while 1:
        # pk = random.randint(1,max_id)
        random_number = random.sample(range(1,max_id+1),1)[0]
        try:
            quiz_instance = Quiz.objects.get(pk=random_number)
        except:
            continue
        check = False
        if quiz_history:
            for history in quiz_history:
                if str(history.quiz_id) == str(quiz_instance):
                    check = True
                    break
        if check:
            continue
        
        queryset = Quiz.objects.filter(pk=random_number)
        # for temp_pk in random_list[1:]:
        #     temp_qs = Quiz.objects.filter(pk=temp_pk)
        #     queryset = queryset.union(temp_qs)
        # queryset = Quiz.objects.filter(pk=pk)
        if queryset:
            return queryset


class QuizListAPIView(ListAPIView):
    serializer_class = QuizSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer,BrowsableAPIRenderer]
    permission_classes = [QuizLimit,]
    
    def get_queryset(self,request):
        return get_random(request)
    
    def post(self, request, *args, **kwargs):
        
        # 1. request.data의 id값 가져오기
        request_id = request.data.get("id")
        # 2. id값으로 model에서 answer가져오기
        real_answer = Quiz.objects.get(pk=request_id)
        # 3. request.data의 answer와 2의 answer 비교
        request_answer = request.data.get("answer")
        if real_answer.answer == request_answer:
            judge = "O"
        else:
            judge = "X"
        # 4. 둘이 값이 같으면 history judge컬럼에 O로 저장
        return_data = {
            "id":request_id,
            "question":request.data.get("question"),
            "judge":judge,
            "real_answer":real_answer.answer
        }
        # 값이 틀리면 X로 저장
        QuizHistory.objects.create(judge=judge,
                                   quiz_id=real_answer,
                                   user_id=request.user)
        
        return Response(return_data, template_name="quiz/quiz.html",)
    
    def list(self, request, *args, **kwargs):
        
        
        history_list = QuizHistory.objects.filter(user_id=request.user).order_by("-create_dt")
        quiz_instance = self.get_queryset(request).first()
        
        data = {
            "history":history_list,
            "quiz":quiz_instance
        }
        
        # queryset = self.filter_queryset(self.get_queryset(request))

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = self.get_serializer(queryset, many=True)
        return Response(data, template_name="quiz/quiz2.html",)
        #return Response({"data":serializer.data}, template_name="quiz/list.html",)
      
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                return render(request, template_name="quiz/quiz3.html",)
    
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
    
class QuizRetrieveAPIView(RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer,BrowsableAPIRenderer]
    permission_classes = [IsAuthenticated,]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data":serializer.data},template_name="quiz/detail.html")
    
    def post(self, request, pk):
        
        # 1. request.data의 id값 가져오기
        request_id = request.data.get("id")
        # 2. id값으로 model에서 answer가져오기
        real_answer = Quiz.objects.get(pk=request_id)
        # 3. request.data의 answer와 2의 answer 비교
        request_answer = request.data.get("answer")
        if real_answer.answer == request_answer:
            judge = "O"
        else:
            judge = "X"
        # 4. 둘이 값이 같으면 history judge컬럼에 O로 저장
        return_data = {
            "id":request_id,
            "question":request.data.get("question"),
            "judge":judge,
            "real_answer":real_answer.answer
        }
        # 값이 틀리면 X로 저장
        QuizHistory.objects.create(judge=judge,
                                   quiz_id=real_answer,
                                   user_id=request.user)
        return Response({"data":return_data}, template_name="quiz/detail.html",)
    
    
    
class QuizHistoryListAPIView(ListAPIView):
    queryset = QuizHistory.objects.all()
    serializer_class = QuizHistorySerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer,BrowsableAPIRenderer]
    
    def list(self, request, *args, **kwargs):
        qs = QuizHistory.objects.filter(user_id=request.user)
        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data":serializer.data},template_name="quiz/history.html",)
    # def list(self,request):
    #     instance = QuizHistory.objects.filter(user_id=request.user).first()
    #     print(instance)
    #     serializer = self.get_serializer(instance)
    #     return Response({"data":serializer.data},template_name="quiz/history.html")
    
class QuizHistoryRetrieveAPIView(RetrieveAPIView):
    queryset = QuizHistory.objects.all()
    serializer_class = QuizHistoryRetrieveSerializer
    
    def get_object(self, pk):
        try:
            return QuizHistory.objects.get(pk=pk)
        except QuizHistory.DoesNotExist:
            raise Http404
        
    def retrieve(self, request, pk):
        instance = self.get_object(pk)
        question = instance.quiz_id
        q= Quiz.objects.filter(question=question).first()
        data = {
            "quiz":q,
            "my_record":instance,
        }
        serializer = self.get_serializer(instance=data)
        return Response(serializer.data)