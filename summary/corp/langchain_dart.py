import requests
import zipfile
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import pprint
from io import BytesIO
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents import load_tools
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

# 기업명으로 corp_code를 검색하는 함수
def get_corp_code(corp_name, crtfc_key):
        request_url = 'https://dart.fss.or.kr/corp/searchExistAll.ax'
        data = {'textCrpNm': corp_name}
        result = requests.post(url=request_url, data=data)

        if result.status_code == 200:
            return result.content.rstrip().decode("utf-8")
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
    crtfc_key =  os.getenv("CRTFC_KEY")
    cp_code = get_corp_code(corp_name=corp_name, crtfc_key=crtfc_key)
    financial_data = get_financial_statement(corp_code=cp_code,crtfc_key=crtfc_key)
      
    columns = list(financial_data[0].keys())
    # print(columns)
    financial_df = pd.DataFrame(financial_data, columns=columns)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_api_key
    
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
def get_corp_answer(agent, question):
    result= agent.run(question)
    
    return result

# 기업에 요약설명하는 함수 
def get_corp_info(corp_name):
    openai_api_key = os.getenv("OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    prompt = PromptTemplate(
        input_variables=["corp_name"],
        template="{corp_name}에 대해서 3 문장으로 요약해줘.",
    )
    
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    
    llmchain = LLMChain(llm=llm, prompt=prompt)
    result = llmchain.run(corp_name)

    return result
if __name__ == '__main__':
    # ROE, PBR, PER
    start = time.time()
    f_agent,_ = get_financial_agent(corp_name='SK하이닉스')
    end = time.time()
    # result = get_info(f_agent, corp_name='삼성전자')
    #result = get_corp_answer(f_agent, question='현재 SK하이닉스 주식이 14만원인데 재무제표를 보고 적절한지 알려주라')
    print(end - start)
    result = get_corp_info("삼성전자")
    print(result)
    
    # print(end_1 - start_1)