import os
import re
import json
import urllib.request
import requests
import time
import multiprocessing
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

# 전처리 함수
def clean_html(x):
  x = re.sub("\&\w*\;","",x)
  x = re.sub("<.*?>","",x)
  x = re.sub(r"\s+", " ", x)  
  return x.strip()

# 날짜 가져오기
def gold_date_crawl(link):
    
    ## 1.
    date_selector = "#wrap_index > main > div > div:nth-child(1) > div > div.info_wrap > div.date"
    
    html = requests.get(link, headers = {"User-Agent": "Mozilla/5.0 "\
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
def gold_news_summary(link):
    main_selector = '#wrap_index > main > div > div:nth-child(1) > div > div.din.din2-12.view_din > div:nth-child(2) > div.box.body_wrap > div.content'
    
    html = requests.get(link, headers = {"User-Agent": "Mozilla/5.0 "\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
    "Chrome/110.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(html.text, "lxml")
    
    
    # 본문 수집
    main = soup.select(main_selector)
    main_lst = [m.text for m in main]
    main_str = "".join(main_lst)
    
    main_str = clean_html(main_str)
    
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,
    chunk_overlap  = 20,
    length_function = len,
    add_start_index = True,
    )
    
    texts = text_splitter.create_documents([main_str])

    openai_api_key = os.getenv("OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_api_key
    embedding_model = OpenAIEmbeddings()
    
    db = Chroma.from_documents(texts, embedding_model)
    
    question = "다음 내용을 한 문단으로 요약해줘"
   
    llm = ChatOpenAI(model_name='gpt-3.5-turbo' ,temperature=0)
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
    result = qa_chain({'query':question})

    return clean_html(result.get('result', ''))

# 관련 기사 json형태로 받아오기
def gold_news_json(keyword):
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
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
            if link.startswith('https://www.bntnews.co.kr'):
                selected_items.append(item)
                count += 1
                if count == 5:
                    break

        json_data['items'] = selected_items
    else:
        print("Error Code:" + rescode)

    return json_data

# 뉴스 요약한 내용 정리
def gold_summarize_news(item):
    
    item['title'] = clean_html(item.get('title', ''))
    item['link'] = clean_html(item.get('link', ''))
    item['summary'] = gold_news_summary(item['link'])
    item['date'] = gold_date_crawl(item['link'])
    item.pop('originallink', None)
    item.pop('pubDate', None)
    item.pop('description', None)
        
    return item

# 병렬 수행
def gold_parallel_process_items(items):
    with multiprocessing.Pool() as pool:
        processed_items = pool.map(gold_summarize_news, items)
    return processed_items

# 최종 결과 반환
def gold_news_info(keyword="금시세"):
    json_data = gold_news_json(keyword)
    items = json_data.get('items', [])

    # 병렬 처리를 통해 각 아이템을 요약
    processed_items = gold_parallel_process_items(items)

    # 필터링된 결과를 반환
    json_data['items'] = processed_items

    return json_data


if __name__=='__main__':
    start = time.time()
    print(gold_news_info())
    end = time.time()
    print(end - start)