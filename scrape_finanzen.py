# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 11:57:56 2024

@author: User
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import time
import datetime


def get_stockinfo():
    ### define Index stock-pool
    urls={
    'https://www.finanzen.net/index/s&p_500/werte': 'USA',
    'https://www.finanzen.net/index/mdax/werte': 'EU',
    'https://www.finanzen.net/index/sdax/werte': 'EU',
    'https://www.finanzen.net/index/dax/40-werte': 'EU',
    #'https://www.finanzen.net/index/euro_stoxx_50': 'EU'
    }
    
    stock_list=[]
    wkn_list=[]
    isin_list=[]
    y_symbol_list=[]
    bid_list=[]
    ask_list=[]
    country_list=[]
    print('1')
    
    ### request website to scrape german and us symbols of the stocks
    for url in urls:
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"}
        r = requests.get(url, headers=headers)
        soup =BeautifulSoup(r.text, 'html.parser')
        pages=len(soup.findAll(class_='pagination__item'))
        if pages<=0:
            pages=1
        
        ### get stock-urls
        url_list=[]
        for i in range(pages):
            r = requests.get(url+'?p='+str(i+1), headers=headers)
            soup =BeautifulSoup(r.text, 'html.parser')
            table=soup.find('div', class_="horizontal-scrolling").findAll('td', class_="table__td")
            for line in table:
                if line.find('a', title=True):
                    stock_list.append(line.text.strip().split('\r\n')[0])
                    url_list.append('https://www.finanzen.net'+line.find('a', href=True)['href'])
            time.sleep(1)
            
        
        ### scrape stock-symbol-infos / single stocks
        for stock_url in url_list: 
            print(stock_url)
            r = requests.get(stock_url, headers=headers)
            soup =BeautifulSoup(r.text, 'html.parser')
            
            elements_dict=dict(zip([soup.find('div', class_="snapshot__badge-bar").find_all(class_='badge__key')[x].text for x in range(len(soup.find('div', class_="snapshot__badge-bar").find_all(class_='badge__key')))], [soup.find('div', class_="snapshot__badge-bar").find_all(class_='badge__value')[x].text for x in range(len(soup.find('div', class_="snapshot__badge-bar").find_all(class_='badge__value')))]))       
            wkn_list.append(elements_dict['WKN'])
            isin_list.append(elements_dict['ISIN'])
            try:
                y_symbol_list.append(elements_dict['Symbol'])
            except: 
                continue
            
            sidebar_container=soup.findAll('table', class_="table table--content-right table--headline-first-col")
            for i in range(len(sidebar_container)):
                if sidebar_container[i].find('a', href="https://g.finanzen.net/lang-schwarz-kursbox-logo"):
                    bid=float(sidebar_container[i].findAll('td', class_='table__td')[1].text.split('/')[0].replace('.', '').replace(',', '.'))
                    ask=float(sidebar_container[i].findAll('td', class_='table__td')[3].text.split('/')[0].replace('.', '').replace(',', '.'))
            bid_list.append(bid)
            ask_list.append(ask)
            country_list.append(urls[url])  
            time.sleep(1)
            
    list_of_metrics=[stock_list, wkn_list, isin_list, y_symbol_list, bid_list, ask_list, country_list]    
    df= pd.DataFrame(list(zip(stock_list, wkn_list, isin_list, y_symbol_list, bid_list, ask_list)),columns =['company','wkn', 'isin', 'y_ticker', 'bid', 'ask'])        
    return list_of_metrics

#test=get_stockinfo()

