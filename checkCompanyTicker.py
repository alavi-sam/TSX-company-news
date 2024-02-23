import pandas as pd
import requests
from bs4 import BeautifulSoup


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
    cond = False
    if toronto:
        city = "Toronto"
    