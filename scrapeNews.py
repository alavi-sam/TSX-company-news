import requests
from bs4 import BeautifulSoup
import os
from glob import glob
import pandas as pd
from checkCompanyTicker import Request
from dataclasses import dataclass



@dataclass
class NewsModel:
    header: str
    url: str



class ScrapeCompanyNews(Request):
    def __init__(self, company_name, comapny_ticker):
        self.compay_ticker = comapny_ticker
        self.compay_name = company_name
        self.news_list = list()


    @staticmethod
    def create_url(ticker):
        return f'https://ca.finance.yahoo.com/quote/{ticker}?.tsrc=fin-srch'


    def get_page(self):
        url = self.create_url(self.company_ticker)
        return self.get(url)
    

    # def get_all_news(self, company_page: requests.Response):
    #     parser = BeautifulSoup(company_page.content, 'html.parser')
    #     news_container = parser.find('div', attrs={'id': 'quoteNewsStream-0-Stream'})
    #     all_news = news_container.find('ul').find_all('li')
    #     for news in all_news:
    #         news_header_section = news.find('h3')
    #         news_url = news_header_section.find('a')
    #         news_header = news_url.find('u')
    #         news_instance = NewsModel(url=news_url['href'], header=news_header.text)            
    #         self.news_list.append(news_instance)
    
