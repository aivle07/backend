# consumers.py
import FinanceDataReader as fdr
import pandas as pd
import json
from asyncio import sleep
from random import randint
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import unquote
import plotly.offline as opy
from .dictionary import name_to_code

def write_color(value, before_day):
    color = ""
    if value > before_day:
        color = "red"
    elif value < before_day:
        color = "blue"
    else:
        color = "black"
    return color


def get_data(param):

    # search_param = "BTC/KRW"
    search_param = param
    period = 100
    
    if period is None:
        period = 5
    else:
        period = int(period)
    try:
        #종목코드가 파라미터일 경우
        search_param = name_to_code[search_param]
        df = fdr.DataReader(search_param)[-300:]    
        #df = df.reset_index().rename(columns={"index": "date"})
        df = df.bfill()
        response_data = df.to_dict(orient='records')
    except Exception as e:
        #회사, 주식명이 파라미터일 경우
        
        # name_to_code = fdr.StockListing('KRX')[['Code', 'Name']]
        # search_param = name_to_code.loc[name_to_code['Name'] == search_param].Code
        # search_param = name_to_code[search_param]
        df = fdr.DataReader(search_param)[-300:]  
        #df = df.reset_index().rename(columns={"index": "date"})
        response_data = df.to_dict(orient='records')
      
    data = []
    # 전날종가
    before_day = round(response_data[-2]['Close'],2)
    # 현재가격
    now_value = round(response_data[-1]['Close'],2)
    now_value_color = write_color(now_value, before_day)
    # 오늘 고가
    today_high = round(response_data[-1]['High'],2)
    today_high_color = write_color(today_high, before_day)
    # 오늘 저가
    today_low = round(response_data[-1]['Low'],2)
    today_low_color = write_color(today_low, before_day)
    # 오늘 거래량
    today_volume = response_data[-1]['Volume']
    # 오늘 시작가격
    today_open = round(response_data[-1]['Open'],2)
    today_open_color = write_color(today_open, before_day)
    # 등락율
    today_change_rate = "None"
    today_change_rate_color = "black"
    if 'Change' in response_data[-1]:
        today_change_rate = response_data[-1]["Change"]
        if today_change_rate > 0:
            today_change_rate_color = "red"
        elif today_change_rate < 0:
            today_change_rate_color = "blue"
        else:
            today_change_rate_color = "black"
        today_change_rate = str(round(today_change_rate * 100,2)) + "%"
    
    # 전일대비 가격변화
    price_change = round(abs(now_value - before_day),2)
    price_change_color = write_color(now_value, before_day)
    today_data = {
        "before_day":before_day,
        "now_value":now_value,
        "now_value_color":now_value_color,
        "today_high":today_high,
        "today_high_color":today_high_color,
        "today_low":today_low,
        "today_low_color":today_low_color,
        "today_volume":today_volume,
        "today_open":today_open,
        "today_open_color":today_open_color,
        "today_change_rate":today_change_rate,
        "today_change_rate_color":today_change_rate_color,
        "price_change":price_change,
        "price_change_color":price_change_color
    }
    #response_data.reverse()
    # for i in response_data[::-1]:
    #     open_data = i['Open']
    #     close_data = i['Close']
    #     data.append(open_data)
    #     data.append(close_data)
    chart = fdr.chart.plot(df)
    chart = opy.plot(chart, output_type='div')
    
    # result = [data, today_data]
    result = [chart, today_data]
    return result
    #return response_data[0]['Close']

class GraphConsumer(AsyncWebsocketConsumer):
    #원래 코드
    async def connect(self):
        # 클라이언트에서 전달한 파라미터
        param = self.scope['query_string']
        #.decode()
        param = unquote(param.decode('utf-8'))
        #print(param)
        await self.accept()
    
        while 1:
            value = get_data(param)
            await self.send(json.dumps({"value":value,
                                        "param":param,
                                        }))
            
            await sleep(1)
            
    async def disconnect(self, code):
        pass