import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import random
from glob import glob
import json

'''
1- Ticker.TO check for Toronto and has price
2- Ticker.V checb for Vancouver and has price


'''



class Request:
    DIRS = glob(os.path.join('UaJson', '*.json')) 

    def _select_ua(self):
        ua_file = random.choice(self.DIRS)
        with open(ua_file, 'r') as f:
            ua = random.choice(json.load(f))['ua']
            while 'Android' in ua or 'iPhone' in ua or 'Tablet' in ua:
                with open(ua_file, 'r') as f:
                    ua = random.choice(json.load(f))['ua']
        return ua

    def get(self, url):
        # ua = self._select_ua()
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        return requests.get(url, headers={'User-Agent': ua})


custom_request = Request()


df = pd.read_csv('TSXV.csv')

def request_company_page(ticker, toronto=True):
    # if ticker == 'VGZ':
    #     print()

    if toronto:
        ticker += '.TO'
    else:
        ticker += '.V'

    response = custom_request.get(f'https://ca.finance.yahoo.com/quote/{ticker}')
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

if __name__ == '__main__':


    os.makedirs('data-tsxv', exist_ok=True)

    list_t = list()
    list_v = list()
    list_error = list()

    for idx, row in df.iterrows():
        company_name = row['Name']
        ticker = row[' Root\nTicker ']
        t_response = request_company_page(ticker)
        v_response = request_company_page(ticker, toronto=False)
        # try:
        try:
            t_cond = check_company(t_response)
        except:
            t_cond = False
            try:
                v_cond = check_company(v_response, toronto=False)
            except:
                v_cond = False

            # print(f'errorrrrr -------- \n https://ca.finance.yahoo.com/quote/{ticker}.TO?.tsrc=fin-srch')

        # try:
        # v_cond = check_company(v_response, toronto=False)
        # except:
        # t_cond = False
        # print(f'errorrrrr -------- \n https://ca.finance.yahoo.com/quote/{ticker}.V?.tsrc=fin-srch')
        
        if t_cond:
            list_t.append({
                'CompanyName': company_name,
                'Ticker': ticker+'.TO'
            })
            print('found {}.TO'.format(ticker))
        else:
            if v_cond:
                list_v.append({
                    'CompanyName': company_name,
                    'Ticker': ticker+'.V'
                })
                print('found {}.V'.format(ticker))

            else:
                # check_company(ticker)
                # check_company(ticker, toronto=False)
                # print('ERRORRRRRR  ', ticker)
                list_error.append({
                    'CompanyName': company_name,
                    'Ticker': ticker
                })

        df_to = pd.DataFrame(list_t)
        df_to.to_csv(os.path.join('data-tsxv', 'TorontoCompanies.csv'))

        df_v = pd.DataFrame(list_v)
        df_v.to_csv(os.path.join('data-tsxv', 'VancouverCompanies.csv'))

        df_error = pd.DataFrame(list_error)
        df_error.to_csv(os.path.join('data-tsxv', 'error.csv'))
        if idx % 10 == 0:
            print(idx, ' searched')

