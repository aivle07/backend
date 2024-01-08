import os
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
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

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

    start = time.time()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}
    html = []
    for url in urls:
        html.append(Document(page_content=requests.get(url,headers=headers).text, metadata={"source": url}))
    end = time.time()
    print('html load : ',end-start)
    
    start = time.time()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=['article'])
    text = docs_transformed[0].page_content
    end = time.time()
    
    print('html parser : ',end-start)
    
    start = time.time()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_api_key

    prompt = PromptTemplate(
        input_variables=["news"],
        template="{news}를 10 문장으로 요약해줘.",
    )
    
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    
    llmchain = LLMChain(llm=llm, prompt=prompt)
    end = time.time()
    
    print('langchain : ',end-start)
    result = llmchain.run(text)
    
    
    return result

# 관련 기사 json형태로 받아오기
def news_json(keyword):
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


if __name__=='__main__':
    start = time.time()
    print(news_info(keyword='SK하이닉스'))
    end = time.time()
    print(end - start)