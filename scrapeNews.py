import requests
from bs4 import BeautifulSoup
import os
from glob import glob
import pandas as pd
from checkCompanyTicker import Request



class ScrapeCompanyNews(Request):
    def __init__(self, company_name, comapny_ticker):
        self.compay_ticker = comapny_ticker
        self.compay_name = company_name


    @staticmethod
    def create_url(ticker):
        return f'https://ca.finance.yahoo.com/quote/{ticker}?.tsrc=fin-srch'


    def get_page(self):
        url = self.create_url(self.company_ticker)
        return self.get(url)
    

    def get_all_news(company_page: requests.Response):
        parser = BeautifulSoup(company_page.content, 'html.parser')
        news_container = parser.find('div', attrs={'id': 'quoteNewsStream-0-Stream'})
        return news_container.find('ul').find_all('li')
    
