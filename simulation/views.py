from django.shortcuts import render, redirect
from .models import *
from datetime import datetime
import FinanceDataReader as fdr
from plotly.offline import plot
from django.contrib.auth.decorators import login_required
from .dictionary import name_to_code

def get_data(param):

    # search_param = "BTC/KRW"
    search_param = param
    period = 1
    
    if period is None:
        period = 5
    else:
        period = int(period)
    try:
        #종목코드가 파라미터일 경우
        df = fdr.DataReader(search_param)[-300:]
        #df = df.reset_index().rename(columns={"index": "date"})
        df = df.bfill()
        #response_data = df.to_dict(orient='records')
    except Exception as e:
        #회사, 주식명이 파라미터일 경우
        
        # name_to_code = fdr.StockListing('KRX')[['Code', 'Name']]
        # search_param = name_to_code.loc[name_to_code['Name'] == search_param].Code
        search_param = name_to_code[search_param]
        df = fdr.DataReader(search_param)[-300:]
        #df = df.reset_index().rename(columns={"index": "date"})
        #response_data = df.to_dict(orient='records')
        
    return df

weekday = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
def index(request):
    param = request.GET.get("param")
    now = datetime.now().strftime("%Y-%m-%d")
    wd = " (" + weekday[datetime.now().weekday()] +") "
    now += wd
    if request.GET.get("commodity") is not None and request.GET.get("count") is not None and request.GET.get("now-value") is not None:
        commodity = request.GET.get("commodity")
        count = request.GET.get("count")
        now_value = request.GET.get("now-value")
        user = request.user
        message = "1이상의 숫자만 입력가능합니다."
        try:
            count = int(count)
        except:
            
            return render(request, "stock/stock1.html", context={"param":commodity,
                                                                 "now":now,
                                                               "message":message})
        if count <= 0:
            return render(request, "stock/stock1.html", context={"param":commodity,
                                                                 "now":now,
                                                               "message":message})
        # 여기에 매수한 것을 db에 넣는 과정이 필요
        Buy.objects.create(user=user, commodity=commodity,
                           count=count, market_value=now_value)
        refresh = True
        return render(request, "stock/stock1.html", context={"param":commodity,
                                                             "now":now,
                                                             "refresh":refresh,})
    try:
        df = get_data(param)
        # chart = fdr.chart.plot(df)
        # chart = plot(chart, output_type='div', include_plotlyjs=False)
        chart = 1
    except:
        search_message = "상품명을 정확히 입력하세요."
        return render(request, "stock/stock1.html", context={"param":param,
                                                               "search_message":search_message,
                                                               "now":now,})
    return render(request, "stock/stock1.html", context={"param":param,
                                                       "chart":chart,
                                                       "now":now,})
@login_required
def my_report(request):
    data = []
    user = request.user
    if request.method == "POST":
        list_item = request.POST.getlist("buy_list")
        print(list_item)
        
        for buy_id in list_item:
            item = Buy.objects.get(id=buy_id)
            item.is_sell = True
            item.save()
            # 상품명 
            commodity = item.commodity
            # 매도시점 시장가
            sell_time_market_value = get_data(commodity)["Close"][-1]
            SellHistory.objects.create(user=user, buy=item, sell_time_market_value=sell_time_market_value)
        
    queryset = Buy.objects.filter(user=user)
    total_calc = []
    # 총 매입금액, 총 평가금액, 총 투자수익률, 총 손익
    total_buy, now_total_buy, total_rate, total_profit_and_loss = 0,0,"0%",0
    for i in queryset:
        if i.is_sell:
            continue
        temp = {}
        temp["id"] = i.id
        # 상품명
        temp["commodity"] = i.commodity
        # 수량
        temp["count"] = i.count
        # 매입시점의 가격
        temp["market_value"] = i.market_value
        temp["create_dt"] = i.create_dt
        temp["user_id"] = i.user
        # 매입가격
        temp["total"] = i.count * i.market_value
        total_buy += temp["total"]

        now_market_value = int(get_data(i.commodity)["Close"][-1]) # 현재시장가
        profit_and_loss = (i.count) * (now_market_value - i.market_value)
        rate = str(round((profit_and_loss / (i.count * i.market_value))*100,2))+"%"
        
        # 현재시장가
        temp["now_market_value"] = now_market_value
        # 평가금액
        temp["now_total"] = now_market_value * i.count
        now_total_buy += temp["now_total"]
        # 수익률
        temp["rate"] = rate
        # 손익
        temp["profit_and_loss"] = profit_and_loss
        total_profit_and_loss += temp["profit_and_loss"]
        
        data.append(temp)
        
    total_temp = {}
    total_temp["total_buy"] = total_buy
    total_temp["now_total_buy"] = now_total_buy
    total_temp["total_profit_and_loss"] = total_profit_and_loss
    if total_buy != 0:
        total_rate = str(round((total_profit_and_loss / (total_buy))*100,2))+"%"
    total_temp["total_rate"] = total_rate
    total_calc.append(total_temp)
    
    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render(request, "stock/stock2.html", context={"data":data,
                                                    "time":now_time,
                                                    "total_calc":total_calc,})