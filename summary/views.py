from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .corp.langchain_dart import *
from .corp.langchain_news import *
from .exchange.exchange_final import *
from .gold.langchain_gold import *
from .gold.langchain_goldnews import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
import FinanceDataReader as fdr
import zipfile
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import pprint
import re
import json
import urllib.request
import requests
import time

agent = None
###### 이 아래는 view ######
#대시보드
def index(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            ## 여기서 모두 결과를 가져온 후 (corp_news)
            # start = time.time()
            # agent,financial_data = get_financial_agent('SK하이닉스')
            # end = time.time()
            # print('agent생성 : ',end-start)
            
            # start = time.time()
            # corp_info = get_corp_info('SK하이닉스')
            # end = time.time()
            # print('기업요약 : ',end-start)
            
            # start = time.time()
            # corp_news = news_info('SK하이닉스')
            # end = time.time()
            # print('뉴스정보추출 : ',end-start)
        
            # start = time.time()
            # chat_answer = get_corp_answer(agent,'재무제표에 대해 알려줘')
            # end = time.time()
            # print('챗봇 답장 : ',end-start)
            
            stock_data = {}
            try:
                #종목코드가 파라미터일 경우
                df = fdr.DataReader('SK하이닉스').sort_index(ascending=False).head()    
                df = df.reset_index().rename(columns={"index": "date"})
                stock_data = df.to_dict(orient='records')
            except Exception as e:
                #회사, 주식명이 파라미터일 경우
                name_to_code = fdr.StockListing('KRX')[['Code', 'Name']]
                filter = name_to_code.loc[name_to_code['Name'] == 'SK하이닉스']
                
                search_param = filter[['Code']].values[0]
                
                df = fdr.DataReader(search_param).sort_index(ascending=False).head()    
                df = df.reset_index().rename(columns={"index": "date"})
                stock_data = df.to_dict(orient='records')
            # 여기에 넣기
            return render(request, 'summary/index.html',
                          {
                        # 'corp_info':corp_info, 
                        #    'corp_news':corp_news['items'],
                        #    'chat_answer':chat_answer,
                        #    'financial_data':financial_data,
                           'stock_data':stock_data,})
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary')

# 부동산
def real_estate(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            return render(request, 'summary/real_estate.html')
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/real_estate')
        
        
# 금        
def gold_rate(request):
    global agent
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
                
        if user:  # 로그인 한 사용자라면
            #gold_news = gold_news_info()
            if agent == None:
                 agent = get_gold_data_agent()
            df_gold = get_gold_data()
            current_gold = df_gold['Close'][-1:].values[0]
            return render(request, 'summary/gold_rate.html',{
               # 'gold_news': gold_news['items'],
                'current_gold': current_gold
                
            })
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/gold_rate')
        

@api_view(('POST',))
def gold_chatbot(request):
    global agent
    user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
    
    if user:
        # gold_agent = get_gold_data_agent()
        question = request.POST.get('data')
        result = get_answer(agent, question=question)
        # print(result)
        return Response({
            'chat_answer': result   
        },status=status.HTTP_200_OK)
    else:  # 로그인이 되어 있지 않다면 
        return redirect('/accounts/login/?next=/summary/gold_rate')
            
# 환율
def exchange_rate(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            ####
            # 여기에 프론트에 넘길 데이터 작성, 함수호출
            ####
            return render(request, 'summary/exchange_rate.html',{
                # 'key' : data
                # 'corp_info' : result
                })
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/exchange_rate')  

# 코인
def coin(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            return render(request, 'summary/coin.html')
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/coin')  
    