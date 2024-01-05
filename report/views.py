from django.shortcuts import render
from report.models import Report
from .f_report_final import get_pdf_report
from .f_report_final import get_pdf_report_answer
from rest_framework.response import Response
from rest_framework import status
import os
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse

openai_api_key = os.getenv("OPENAI_API_KEY")
db = None
summary = None
# Create your views here.
@login_required
def report(request):
    global db, summary
    
    if request.method == "GET":
        # 1. Report 디비에서 가장 최근의 pdf파일을 가져온다.
        report_instance = Report.objects.last()
        file = os.path.join(settings.MEDIA_ROOT, str(report_instance.file))
        
        # 2. get_pdf_report 메소드에 파일이름과 api_key를 매개변수로 넘겨준다
        if db == None:
            db = get_pdf_report(openai_api_key, file)
            question = "금융 리포트를 한 페이지로 요약해줘"
            summary = get_pdf_report_answer(db, question)
            
        # 3. context에 요약된 내용, Report 인스턴스를 넣어준다.
        context = {"report":report_instance,
                   "summary":summary,}
        
        return render(request, 'report/report.html', context=context)
    else:
        
        question = request.POST.get('data')
        result = get_pdf_report_answer(db, question=question)
        # print(result)
        return JsonResponse({
            'chat_answer':result
        },status=status.HTTP_200_OK)
        
    
    
   