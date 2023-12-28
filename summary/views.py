from urllib.parse import urlencode
from django.shortcuts import redirect, render
import requests
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
import multiprocessing
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from io import BytesIO
import FinanceDataReader as fdr
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents import load_tools
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

################## NEWS
# 전처리 함수
def clean_html(x):
  x = re.sub("\&\w*\;","",x)
  x = re.sub("<.*?>","",x)
  x = re.sub(r"\s+", " ", x)  
  return x.strip()

# 날짜 가져오기
def date_crawl(all_hrefs):
    
    ## 1.
    date_selector = "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans"\
    "> div.media_end_head_info_datestamp > div:nth-child(1) > span"
    
    html = requests.get(all_hrefs, headers = {"User-Agent": "Mozilla/5.0 "\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
    "Chrome/110.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(html.text, "lxml")
    
    
    # 날짜 수집
    date = soup.select(date_selector)
    date_lst = [d.text for d in date]
    date_str = "".join(date_lst)
    
    date_str = clean_html(date_str)
    
    return date_str

# 본문 요약하기
def news_summary(link):
    urls = [link]

    loader = AsyncChromiumLoader(urls=urls)
    html = loader.load()

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=['article'])
    text = docs_transformed[0].page_content

    os.environ["OPENAI_API_KEY"] = ''

    prompt = PromptTemplate(
        input_variables=["news"],
        template="{news}를 3 문장으로 요약해줘.",
    )
    
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    
    llmchain = LLMChain(llm=llm, prompt=prompt)
    result = llmchain.run(text)

    return result

# 관련 기사 json형태로 받아오기
def news_json(keyword):
    client_id = 'ePeuyLaOAwP42TK261ty'
    client_secret = 'saGpbRdxCh'
    encText = urllib.parse.quote(keyword)
    # JSON 결과, 검색결과 정렬방법 -> 정확도순 내림차순, 10개의 뉴스를 가져오기
    url = 'https://openapi.naver.com/v1/search/news.json?query=' + encText  + '&display=10' + '&sort=sim'
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        decoded_content = response_body.decode('utf-8')
        json_data = json.loads(decoded_content)
        json_data.pop('lastBuildDate', None)
        json_data.pop('total', None)
        json_data.pop('start', None)
        json_data.pop('display', None)

        # 필요한 조건을 만족하는 아이템 중 상위 5개만 선택
        selected_items = []
        count = 0
        for item in json_data.get('items', []):
            link = clean_html(item.get('link', ''))
            if link.startswith('https://n.news.naver.com'):
                selected_items.append(item)
                count += 1
                if count == 5:
                    break

        json_data['items'] = selected_items

    else:
        print("Error Code:" + rescode)

    return json_data

# 뉴스 요약한 내용 정리
def summarize_news(item):
    
    item['title'] = clean_html(item.get('title', ''))
    item['link'] = clean_html(item.get('link', ''))
    item['summary'] = news_summary(item['link'])
    item['date'] = date_crawl(item['link'])
    item.pop('originallink', None)
    item.pop('pubDate', None)
    item.pop('description', None)
        
    return item

# 병렬 수행
def parallel_process_items(items):
    with multiprocessing.Pool() as pool:
        processed_items = pool.map(summarize_news, items)
    return processed_items

# 최종 결과 반환
def news_info(keyword):
    json_data = news_json(keyword)
    items = json_data.get('items', [])

    # 병렬 처리를 통해 각 아이템을 요약
    processed_items = parallel_process_items(items)

    # 필터링된 결과를 반환
    json_data['items'] = processed_items

    return json_data
################## NEWS END




################## CORP BEGIN

# 기업명으로 corp_code를 검색하는 함수
def get_corp_code(corp_name, crtfc_key):
        request_url = 'https://opendart.fss.or.kr/api/corpCode.xml'
        parameters = {'crtfc_key': crtfc_key}
        result = requests.get(url=request_url, params=parameters)

        if result.status_code == 200:
            with BytesIO(result.content) as zip_content:
                with zipfile.ZipFile(zip_content, 'r') as z:
                    xml_content = z.read(z.namelist()[0])

                root = ET.fromstring(xml_content)

                for company in root.iter('list'):
                    if corp_name.strip() == company.find('corp_name').text.strip():
                        return company.find('corp_code').text

            return None
        else:
            return None

# 재무제표 불러오는 함수
def get_financial_statement(corp_code, crtfc_key, bsns_year='2023', reprt_code='11014'):
        request_url = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'
        parameters = {
            'crtfc_key': crtfc_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code
        }

        result = requests.get(url=request_url, params=parameters)

        if result.status_code == 200:
            data = result.json()

            if 'list' in data:
                selected_data = {
                    # 'corp_code': data.get('corp_code', ''),
                    # 'corp_name': data.get('corp_name', ''),
                    # 'bsns_year': data.get('bsns_year', ''),
                    'financial_data': data.get('list', [])
                }
                
                return selected_data['financial_data']
            else:
                return None
        else:
            return None

# 재무제표 agent 생성하는 함수
def get_financial_agent(corp_name):
    crtfc_key = '70b7fc05ddead0a3214c5338845dba340ab2e5d7'
    cp_code = get_corp_code(corp_name=corp_name, crtfc_key=crtfc_key)
    financial_data = get_financial_statement(corp_code=cp_code,crtfc_key=crtfc_key)
      
    columns = list(financial_data[0].keys())
    # print(columns)
    financial_df = pd.DataFrame(financial_data, columns=columns)
    
    os.environ["OPENAI_API_KEY"] = ''
    
    llm_1 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    agent_1 = create_pandas_dataframe_agent(
        llm_1,
        financial_df,
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        # extra_tools=tools
    )
    
    return agent_1,financial_data

# 질문에 대한 응답 불러오는 함수
def get_answer(agent, question):
    result= agent.run(question)
    
    return result

def get_info(corp_name):
    # question = f'{corp_name}가 어떤 기업인지 설명해줘'
    # result = agent.run(question)
    os.environ["OPENAI_API_KEY"] = ''

    prompt = PromptTemplate(
        input_variables=["corp_name"],
        template="{corp_name}에 대해서 3 문장으로 요약해줘.",
    )
    
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    
    llmchain = LLMChain(llm=llm, prompt=prompt)
    result = llmchain.run(corp_name)

    return result
################## CORP END

###### 이 아래는 view ######
#대시보드
def index(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            ## 여기서 모두 결과를 가져온 후 (corp_news)
            start = time.time()
            agent,financial_data = get_financial_agent('SK하이닉스')
            end = time.time()
            print('agent생성 : ',end-start)
            
            start = time.time()
            corp_info = get_info('SK하이닉스')
            end = time.time()
            print('기업요약 : ',end-start)
            
            start = time.time()
            corp_news = news_info('SK하이닉스')
            end = time.time()
            print('뉴스정보추출 : ',end-start)
        
            start = time.time()
            chat_answer = get_answer(agent,'재무제표에 대해 알려줘')
            end = time.time()
            print('챗봇 답장 : ',end-start)
            
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
                          {'corp_info':corp_info, 
                           'corp_news':corp_news['items'],
                           'chat_answer':chat_answer,
                           'financial_data':financial_data,
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
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            return render(request, 'summary/gold_rate.html')
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/accounts/login/?next=/summary/gold_rate')  
# 환율
def exchange_rate(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  # 로그인 한 사용자라면
            return render(request, 'summary/exchange_rate.html')
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
    