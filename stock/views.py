import FinanceDataReader as fdr
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
 
def GetStockCode():
    #외국 거래소
    market_list = ['NASDAQ', 'NYSE', 'AMEX', 'S&P500',]# 'SSE', 'SZSE', 'HKEX', 'TSE']
    name_to_code = pd.DataFrame()
    for market in market_list:
        tmp = fdr.StockListing(market)[['Symbol','Name']]
        name_to_code = pd.concat([name_to_code, tmp])
    return name_to_code
 
@api_view(('GET',))
def StockRetrieveAPI(request):
    search_param = request.GET.get('search_param')
    period = request.GET.get('period')
    if period is None:
        period = 5
    else:
        period = int(period)
    try:
        #종목코드가 파라미터일 경우
        df = fdr.DataReader(search_param).sort_index(ascending=False).head(period)    
        df = df.reset_index().rename(columns={"index": "date"})
        response_data = df.to_dict(orient='records')
    except Exception as e:
        #회사, 주식명이 파라미터일 경우
        name_to_code = fdr.StockListing('KRX')[['Code', 'Name']]
        search_param = name_to_code.loc[name_to_code['Name'] == search_param].Code
                
        df = fdr.DataReader(search_param).sort_index(ascending=False).head(period)    
        df = df.reset_index().rename(columns={"index": "date"})
        response_data = df.to_dict(orient='records')
       
    return Response(response_data, status=status.HTTP_200_OK,)

