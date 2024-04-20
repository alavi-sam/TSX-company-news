import requests
from bs4 import BeautifulSoup
import os
from glob import glob
import pandas as pd
# from checkCompanyTicker import Request
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time



class Request:
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")   

    
    def __init__(self):
        self.service = Service('chromedriver')
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
    

    def scroll(self):
        prev_height = -1
        window_height = self.driver.execute_script("return window.innerHeight")
        max_scrolls = 1000000
        scroll_count = 0

        while scroll_count < max_scrolls:
            self.driver.execute_script(f"window.scrollTo(0, {window_height});")
            window_height *= 2
            time.sleep(1)  # give some time for new results to load
            new_height = self.driver.execute_script("return window.pageYOffset")
            if new_height == prev_height:
                break
            prev_height = new_height
            scroll_count += 1


    def get(self, url, scroll=True):
        self.driver.get(url)
        time.sleep(3)
        if scroll:
            self.scroll()
        reponse = self.driver.page_source
        # self.driver.close()
        return reponse




@dataclass
class NewsModel:
    header: str
    url: str



class ScrapeCompanyNews(Request):
    def __init__(self, company_name, comapny_ticker):
        super().__init__()
        self.company_ticker = comapny_ticker
        self.company_name = company_name
        self.news_list = list()


    @staticmethod
    def create_url(ticker):
        return f'https://ca.finance.yahoo.com/quote/{ticker}?.tsrc=fin-srch'


    def get_page(self):
        url = self.create_url(self.company_ticker)
        return self.get(url)
    

    def get_all_news(self, company_page: requests.Response):
        parser = BeautifulSoup(company_page, 'html.parser')
        news_container = parser.find('div', attrs={'id': 'quoteNewsStream-0-Stream'})
        all_news = news_container.find('ul').find_all('li')
        for news in all_news:
            if news.find('div', attrs={'class': 'controller gemini-ad native-ad-item Feedback Pos(r)'}):
                continue
            try:
                news_header_section = news.find('h3')
                news_url = news_header_section.find('a')
                news_header = news_url.text
                news_instance = NewsModel(url=news_url['href'], header=news_header)            
                self.news_list.append(news_instance)
            except AttributeError:
                continue


        return self.news_list
    


class ScrapeNews(Request):
    def __init__(self, header, url):
        super().__init__()
        self.header = header
        self.url = url


    def get_news(self):
        response = self.get('https://ca.finance.yahoo.com' + self.url, scroll=False)
        parser = BeautifulSoup(response, 'html.parser')
        if parser.find('div', {'class': 'con-wizard'}):
            consent_container = self.driver.find_element(by=By.XPATH, value="//div[@class='con-wizard']")
            consent_container.find_element(By.XPATH, "//button[@class='btn secondary accept-all consent_reject_all_2']").click()
        parser = BeautifulSoup(self.driver.page_source, 'html.parser')
        article_container = parser.find('article', attrs={'class': 'caas-container'})
        article_body = article_container.find('div', attrs={'class': 'caas-body'})        
        paragraphs = article_body.find_all('p')
        content = str()
        content += 'https://ca.finance.yahoo.com' + self.url + '\n'
        for paragraph in paragraphs:
            content += paragraph.text + '\n'

        return content
    


if __name__ == '__main__':
    # df = pd.read_csv(os.path.join('data-tsxv', 'VancouverCompanies.csv'))
    df = pd.read_excel('GSD 10-Baggers.xlsx', sheet_name='Sheet1')
    os.makedirs('data-10-b', exist_ok=True)
    for i, row in df.iterrows():
        if not os.path.isdir(os.path.join('data-10-b', row[1])):
            os.makedirs(os.path.join('data-10-b', row[1]))
        scrape_companies = ScrapeCompanyNews(comapny_ticker=row[1], company_name=row[0])
        company_page = scrape_companies.get_page()
        news = scrape_companies.get_all_news(company_page)
        for i, new in enumerate(news):
            # new.header = new.header.replace(':', '').replace('/', '').replace('\\', '').replace('"', '').replace("'", '').replace('?', '').replace('%', '').replace(',', '').replace(';', '').replace('.', '').replace('’', '').replace('\n', '').replace('>', '').replace('<', '').replace('*', '')
            
            with open('ScrapedNews.txt', 'r') as f:
                scraped_news = set([line.strip() for line in f.readlines()])
            if not f'{row[1]}  {new.header}' in scraped_news:
                scrape_news = ScrapeNews(header=new.header, url=new.url)
                news_content = scrape_news.get_news()
                news_content = news_content.encode('utf-8')
                address = os.path.join(os.getcwd(), 'data-10-b', row[1], new.header)
                print(row[1], new.header)
                with open(os.path.join('data-10-b', row[1], str(i) + '.txt'), 'wb') as f:
                    f.write(news_content)

                with open('ScrapedNews.txt', 'a') as f:
                    f.write(f'{row[1]}  {new.header}\n')
            else:
                print('passed', new.header)

    
