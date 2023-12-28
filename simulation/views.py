from django.shortcuts import render, redirect
from .models import *
from datetime import datetime
import FinanceDataReader as fdr

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
        df = fdr.DataReader(search_param).sort_index(ascending=False).head(period)    
        df = df.reset_index().rename(columns={"index": "date"})
        df = df.bfill()
        response_data = df.to_dict(orient='records')
    except Exception as e:
        #회사, 주식명이 파라미터일 경우
        
        name_to_code = fdr.StockListing('KRX')[['Code', 'Name']]
        search_param = name_to_code.loc[name_to_code['Name'] == search_param].Code
                
        df = fdr.DataReader(search_param).sort_index(ascending=False).head(period)    
        df = df.reset_index().rename(columns={"index": "date"})
        response_data = df.to_dict(orient='records')
        
    return response_data[0]["Close"]

def index(request):
    param = request.GET.get("param")
    
    if request.GET.get("commodity") is not None and request.GET.get("count") is not None and request.GET.get("now-value") is not None:
        commodity = request.GET.get("commodity")
        count = request.GET.get("count")
        now_value = request.GET.get("now-value")
        user = request.user
        message = "1이상의 숫자만 입력가능합니다."
        try:
            count = int(count)
        except:
            
            return render(request, "simulation.html", context={"param":commodity,
                                                               "message":message})
        if count <= 0:
            return render(request, "simulation.html", context={"param":commodity,
                                                               "message":message})
        # 여기에 매수한 것을 db에 넣는 과정이 필요
        Buy.objects.create(user=user, commodity=commodity,
                           count=count, market_value=now_value)
        
        return render(request, "simulation.html", context={"param":commodity})
    try:
        get_data(param)
    except:
        search_message = "상품명을 정확히 입력하세요."
        return render(request, "simulation.html", context={"param":param,
                                                               "search_message":search_message})
    return render(request, "simulation.html", context={"param":param})

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
            sell_time_market_value = get_data(commodity)
            SellHistory.objects.create(user=user, buy=item, sell_time_market_value=sell_time_market_value)
        
    queryset = Buy.objects.filter(user=user)
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

        now_market_value = int(get_data(i.commodity)) # 현재시장가
        profit_and_loss = (i.count) * (now_market_value - i.market_value)
        rate = str(round((profit_and_loss / (i.count * i.market_value))*100,2))+"%"
        
        # 현재시장가
        temp["now_market_value"] = now_market_value
        # 평가금액
        temp["now_total"] = now_market_value * i.count
        # 수익률
        temp["rate"] = rate
        # 손익
        temp["profit_and_loss"] = profit_and_loss
        
        data.append(temp)
    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render(request, "myreport.html", context={"data":data,
                                                    "time":now_time})