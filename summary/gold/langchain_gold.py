import FinanceDataReader as fdr
import os
import time
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 금 정보 agent 생성함수
def get_gold_data_agent():
    df_gold = get_gold_data()

    
    openai_api_key = os.getenv("OPENAI_API_KEY")

    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    agent = create_pandas_dataframe_agent(
        llm,
        df_gold,
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True,
        # extra_tools=tools
    )
    
    return agent

def get_gold_data():
    df_gold = fdr.DataReader('GC=F',"2023-12-01")
    
    nan_rows = df_gold[df_gold.isna().any(axis=1)].index

    df_gold.dropna(inplace=True)
    df_gold.reset_index(inplace=True)
    if df_gold['Date'][-1:].values[0] != datetime.today().strftime("%Y-%m-%d"):
        df_gold['Date'][-1:].values[0] = datetime.today().strftime("%Y-%m-%d")
    
    df_usa = fdr.DataReader('USD/KRW',"2023-12-01")
    
    df_usa.drop(nan_rows, inplace=True)
    df_usa.reset_index(inplace=True)
    
    df_gold['Open'] = df_gold['Open'] / 31.1034768 * df_usa['Open'] / 0.9999
    df_gold['High'] = df_gold['High'] / 31.1034768 * df_usa['High'] / 0.9999
    df_gold['Low'] = df_gold['Low'] / 31.1034768 * df_usa['Low'] / 0.9999
    df_gold['Close'] = df_gold['Close'] / 31.1034768 * df_usa['Close'] / 0.9999
    df_gold = df_gold.round(2)
    df_gold['Date'] = pd.to_datetime(df_gold['Date'])
    df_gold['Year'] = df_gold['Date'].dt.year
    df_gold['Month'] = df_gold['Date'].dt.month
    df_gold['Day'] = df_gold['Date'].dt.day
    # df_gold.drop(columns=['Date'])
    return df_gold

# 금 챗봇 결과 생성
def get_answer(agent, question):
    result= agent.run(question)
    
    return result

if __name__=='__main__':
    start_1 = time.time()
    gold_agent = get_gold_data_agent()
    end_1 = time.time()
    question = '12월 달 종가가 가장 낮은 날은 언제야?'
    start_2 = time.time()
    result = get_answer(gold_agent, question=question)
    end_2 = time.time()
    print(result)
    print('데이터, 에이전트 생성 시간:',end_1 - start_1)
    print('답변 나오는 시간:',end_2 - start_2)