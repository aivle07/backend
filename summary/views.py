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
import plotly.offline as opy
import plotly.graph_objects as go
import plotly

agent = None
###### 이 아래는 view ######
@api_view(('POST',))
def search_corp(request):
    global agent
    user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
    
    if user:
        corp_name = request.POST.get('corp_name')
        if agent == None:
            agent, _ =  get_financial_agent(corp_name)
            print('에이전트 생성완료')
        # 여기서 모두 결과를 가져온 후 (corp_news)
        
        start = time.time()
        corp_info = get_corp_info(corp_name)
        end = time.time()
        print('기업요약 : ',end-start)
        
        start = time.time()
        corp_news = news_info(corp_name)
        end = time.time()
        print('뉴스정보추출 : ',end-start)
    
        
        crtfc_key = os.getenv("CRTFC_KEY")
        financial_data = get_financial_statement(get_corp_code(corp_name,crtfc_key),crtfc_key)
        
        stock_data = {            
            'KS11' : fdr.DataReader('KS11').tail(2).to_dict(orient='records'), # KOSPI 지수 (KRX)
            'KQ11' : fdr.DataReader('KQ11').tail(2).to_dict(orient='records'), # KOSDAQ 지수 (KRX)
            'KS200' : fdr.DataReader('KS200').tail(2).to_dict(orient='records'), # KOSPI 200 (KRX)
        }
        try:
            #종목코드가 파라미터일 경우
            df = fdr.DataReader(financial_data[0]['stock_code']).sort_index(ascending=False).head()    
            df = df.reset_index().rename(columns={"index": "date"})
            
        except Exception as e:
            #회사, 주식명이 파라미터일 경우
            name_to_code = fdr.StockListing('KRX')[['Code', 'Name']]
            filter = name_to_code.loc[name_to_code['Name'] == corp_name]
            
            search_param = filter[['Code']].values[0]
            
            df = fdr.DataReader(search_param).sort_index(ascending=False).head()    
            df = df.reset_index().rename(columns={"index": "date"})
        
        
        # 재무제표 
        fin_data = []
        for data in financial_data:
            tmp = {}
            # 이름
            tmp['name'] =  data['account_nm']
            # 금년
            tmp['thisyear'] = int(data['thstrm_amount'].replace(',',''))//1000
            # 작년
            tmp['lastyear'] = int(data['frmtrm_amount'].replace(',',''))//1000
            fin_data.append(tmp)
        
        chart = fdr.chart.plot(df)
        chart.update_layout(
            autosize=False,
            width=300,
            height=300,
        )
        chart = opy.plot(chart,output_type='div',config=dict(
                    displayModeBar=False
                ))

        return Response({
            'corp_info':corp_info, 
            'corp_news':corp_news['items'],
            'stock_data' : stock_data,
            'chart': chart,
            'fin_data':fin_data,
        },status=status.HTTP_200_OK)
    else:  # 로그인이 되어 있지 않다면 
        return redirect('/accounts/login/?next=/summary')

            
#기업 대시보드
def index(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            
            # 여기에 넣기
            return render(request, 'summary/index.html')
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary')
        
@api_view(('POST',))
def corp_chatbot(request):
    global agent
    user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
    
    if user:
        
        question = request.POST.get('data')
        result = get_corp_answer(agent=agent, question=question)
        # print(result)
        return Response({
            'chat_answer': result   
        },status=status.HTTP_200_OK)
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
            gold_news = gold_news_info()
            if agent == None:
                 agent = get_gold_data_agent()
            df_gold = get_gold_data()
            current_gold = df_gold['Close'][-1:].values[0]
            
            return render(request, 'summary/gold_rate.html',{
                'gold_news': gold_news['items'],
                'current_gold': current_gold,
                'gold_data' : df_gold.to_dict(orient='records'),
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
    global agent
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        
        if user:  # 로그인 한 사용자라면
            # TESTING
            if agent == None:
                agent = get_exchange()
            exchange_news = news_info(keyword='환율')
            dollor, yen = get_exchange_data()
            current_dollor = dollor['Close'][-1:].values[0]
            current_yen = yen['Close'][-1:].values[0]
            current_dollor_round = round(current_dollor, 2)
            current_yen_round_100 = round(current_yen * 100, 2)
            dollor = dollor.tail(30).reset_index()
            yen = yen.tail(30).reset_index()
            return render(request, 'summary/exchange_rate.html',{
                'exchange_news':exchange_news['items'],
                'current_dollor':current_dollor,
                'current_yen':current_yen,
                'current_dollor_round':current_dollor_round,
                'current_yen_round_100':current_yen_round_100,
                'dollor':dollor.to_dict(orient='records'),
                'yen':yen.to_dict(orient='records'),
                })
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/exchange_rate')
        
@api_view(('POST',))
def exchange_chatbot(request):
    global agent
    user = request.user.is_authenticated
    
    if user:
        question = request.POST.get('data')
        result = get__exchange_answer(agent, question=question)
        # print(result)
        return Response({
            'chat_answer':result
        },status=status.HTTP_200_OK)
    else:
        return redirect('/accounts/login/?next=/summary/exchange_rate')
    

# 코인
def coin(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            return render(request, 'summary/coin.html')
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/coin')  
    