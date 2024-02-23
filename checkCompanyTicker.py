import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

'''
1- Ticker.TO check for Toronto and has price
2- Ticker.V checb for Vancouver and has price


'''




df = pd.read_csv('TSX.csv')

def request_company_page(ticker, toronto=True):
    if toronto:
        ticker += '.TO'
    else:
        ticker += '.V'

    response = requests.get(f'https://ca.finance.yahoo.com/quote/{ticker}?.tsrc=fin-srch')
    return response


def check_company(response, toronto=True):
    parser = BeautifulSoup(response.content, 'html.parser')
    location = parser.find('div', attrs={'class': 'C($tertiaryColor) Fz(12px)'}).find('span').text.split('-')[0].strip()
    regular_price = parser.find('fin-streamer', attrs={'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
    cond = False
    if toronto:
        city = "Toronto"
    else:
        city = 'TSXV'
    
    if location == city and float(regular_price) > 0:
        cond = True

    return cond

os.makedirs('data', exist_ok=True)

list_t = list()
list_v = list()

for idx, row in df.iterrows():
    company_name = row['Name']
    ticker = row['Root\nTicker']
    t_response = request_company_page(ticker)
    v_response = request_company_page(ticker, toronto=False)
    t_cond = check_company(t_response)
    v_cond = check_company(v_response, toronto=False)
    
    if t_cond:
        list_t.append({
            'CompanyName': company_name,
            'Ticker': ticker+'.TO'
        })
    if v_cond:
        list_v.append({
            'CompanyName': company_name,
            'Ticker': ticker+'.V'
        })

    if idx % 10 == 0:
        df_to = pd.DataFrame(list_t)
        df_to.to_csv(os.path.join('data', 'TorontoCompanies.csv'))

        df_v = pd.DataFrame(list_v)
        df_v.to_csv(os.path.join('data', 'VancouverCompanies.csv'))

