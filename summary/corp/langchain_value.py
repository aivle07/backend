import requests
import zipfile
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import pprint
import FinanceDataReader as fdr
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
def get_selected_financial_data(corp_code, crtfc_key, bsns_year='2023', reprt_code='11014'):
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
            # 필요한 항목만 선택
            selected_data = [
                {
                    'account_nm': item['account_nm'],
                    'thstrm_dt': item['thstrm_dt'],
                    'thstrm_amount': item['thstrm_amount']
                }
                for item in data['list']
                if item['account_nm'] in ['자산총계', '부채총계', '당기순이익', '자본총계']
            ]

            return selected_data
        else:
            return None
    else:
        return None
        
# 발행주식수 불러오는 함수
def get_stock(corp_code, crtfc_key, bsns_year='2023', reprt_code='11014'):
    request_url = 'https://opendart.fss.or.kr/api/stockTotqySttus.json'
    params = {
        'crtfc_key': crtfc_key,
        'corp_code' : corp_code,
        'bsns_year' : bsns_year,
        'reprt_code' : reprt_code,
    }
    
    result = requests.get(url=request_url, params=params)
    
    if result.status_code == 200:
        data = result.json()

        if 'list' in data:
            # 'SE' 합계에 해당하는 데이터 찾기
            se_data_1 = next(item for item in data['list'] if item.get('se') == '합계')
            se_data_2 = next(item for item in data['list'] if item.get('se') == '보통주')
            # 'istc_totqy' 값 가져오기
            istc_totqy_value_1 = se_data_1.get('istc_totqy')
            istc_totqy_value_2 = se_data_2.get('istc_totqy')
            return istc_totqy_value_1, istc_totqy_value_2
        else:
            return None
    else:
        return None
        
def get_financial_values(corp_name):
    crtfc_key =  os.getenv("CRTFC_KEY")
    cp_code = get_corp_code(corp_name=corp_name, crtfc_key=crtfc_key)
    
    # 2023년 2분기 재무제표 데이터
    financial_data_2 = get_selected_financial_data(corp_code=cp_code,crtfc_key=crtfc_key,reprt_code='11012')
    columns = list(financial_data_2[0].keys())
    financial_df_2 = pd.DataFrame(financial_data_2, columns=columns)
    financial_df_2.drop_duplicates(subset='account_nm', keep='last', inplace=True)
    financial_df_2.reset_index(drop=True, inplace=True)
    
    # 2023년 3분기 재무제표 데이터
    financial_data_3 = get_selected_financial_data(corp_code=cp_code,crtfc_key=crtfc_key,reprt_code='11014')
    columns = list(financial_data_3[0].keys())
    financial_df_3 = pd.DataFrame(financial_data_3, columns=columns)
    financial_df_3.drop_duplicates(subset='account_nm', keep='last', inplace=True)
    financial_df_3.reset_index(drop=True, inplace=True)
    
    # 발행된 주식수 값
    stock_n, stock_n_2 = get_stock(corp_code=cp_code,crtfc_key=crtfc_key,reprt_code='11012')
    stock_n = float(stock_n.replace(',', ''))
    stock_n_2 = float(stock_n_2.replace(',', ''))
    # 주가
    
    # 순자산 계산
    # '자산총계'와 '부채총계'를 찾아 순자산 계산
    total_assets_2 = float(financial_df_2[financial_df_2['account_nm'] == '자산총계']['thstrm_amount'].iloc[0].replace(',', ''))
    total_liabilities_2 = float(financial_df_2[financial_df_2['account_nm'] == '부채총계']['thstrm_amount'].iloc[0].replace(',', ''))
    net_asset_2 = total_assets_2 - total_liabilities_2
    
    total_assets_3 = float(financial_df_3[financial_df_3['account_nm'] == '자산총계']['thstrm_amount'].iloc[0].replace(',', ''))
    total_liabilities_3 = float(financial_df_3[financial_df_3['account_nm'] == '부채총계']['thstrm_amount'].iloc[0].replace(',', ''))
    net_asset_3 = total_assets_3 - total_liabilities_3

    # 순이익 = 당기순이익
    net_profit_2 = float(financial_df_2[financial_df_2['account_nm'] == '당기순이익']['thstrm_amount'].iloc[0].replace(',', ''))
    net_profit_3 = float(financial_df_3[financial_df_3['account_nm'] == '당기순이익']['thstrm_amount'].iloc[0].replace(',', ''))
    
    # 자기자본
    equity_2 = float(financial_df_2[financial_df_2['account_nm'] == '자본총계']['thstrm_amount'].iloc[0].replace(',', ''))
    equity_3 = float(financial_df_3[financial_df_3['account_nm'] == '자본총계']['thstrm_amount'].iloc[0].replace(',', ''))
    
    # 주당순자산가치 (NAVPS) = 순자산 / 발행된 주식수
    navps_2 = net_asset_2 / stock_n
    navps_3 = net_asset_3 / stock_n
    
    # ------------------------위에 값들로 BPS, EPS, ROE, PER, PBR 구하기
    # BPS =  (순자산 / 발행된 주식 수) 보통 주
    bps_2 =  round(net_asset_2 / stock_n_2, 2)
    bps_3 =  round(net_asset_3 / stock_n_2, 2)
    
    # EPS = (순이익 / 발행된 주식 수) 보통 주 == 주당순이익
    eps_2 = round(net_profit_2 / stock_n_2, 2)
    eps_3 = round(net_profit_3 / stock_n_2, 2)
    
    # ROE = (순이익 / 자기자본) x 100
    roe_2 = round((net_profit_2 / equity_2) * 100, 2)
    roe_3 = round((net_profit_3 / equity_3) * 100, 2)

    return financial_data_3, financial_df_3, stock_n

if __name__ == '__main__':
    f_data,f_df,s_n = get_financial_values(corp_name='KT')
    print(f_df)
    